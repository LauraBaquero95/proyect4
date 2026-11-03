# -*- coding: utf-8 -*-
"""
Módulo: operaciones.py
Propósito: simular 12 operaciones completas (válidas e inválidas) para demostrar que
           el sistema continúa funcionando aun cuando ocurren errores.
"""

from src.modelos.alquiler_equipo import AlquilerEquipo
from src.modelos.asesoria import AsesoriaEspecializada
from src.modelos.reserva_sala import ReservaSala
from src.utilidades.logger import ARCHIVO_LOG, obtener_logger

_log = obtener_logger()


def _reportar(gestor, exito, contadores):
    """Imprime el resultado de una operación y actualiza los contadores."""
    if exito:
        contadores["exitosas"] += 1
        print("   -> OK: operación exitosa.")
    else:
        contadores["rechazadas"] += 1
        # El error ya fue registrado en el log; aquí solo se informa y se continúa.
        print(f"   -> ERROR CONTROLADO: {gestor.ultimo_error}")


def ejecutar_simulacion(gestor):
    """Ejecuta las 12 operaciones en orden sobre el gestor recibido."""
    contadores = {"exitosas": 0, "rechazadas": 0}

    print("=" * 70)
    print(" SOFTWARE FJ - SIMULACIÓN DE OPERACIONES")
    print("=" * 70)

    # ---- 1. Cliente válido -------------------------------------------------
    print("\n[1] Registro de un cliente con datos válidos")
    r = gestor.registrar_cliente(identificador="C-001", nombre="Ana Pérez",
                                 correo="ana.perez@correo.com", telefono="3001234567")
    _reportar(gestor, r is not None, contadores)

    # ---- 2. Cliente con correo inválido ------------------------------------
    print("\n[2] Registro de un cliente con correo inválido")
    r = gestor.registrar_cliente(identificador="C-002", nombre="Carlos Gómez",
                                 correo="carlos.gomez@", telefono="3109876543")
    _reportar(gestor, r is not None, contadores)

    # ---- 3. Cliente sin el parámetro 'nombre' ------------------------------
    print("\n[3] Registro de un cliente sin el parámetro obligatorio 'nombre'")
    r = gestor.registrar_cliente(identificador="C-003",
                                 correo="sin.nombre@correo.com", telefono="3151112233")
    _reportar(gestor, r is not None, contadores)

    # ---- 4. Sala válida ----------------------------------------------------
    print("\n[4] Creación de una sala válida")
    r = gestor.registrar_servicio(ReservaSala, identificador="S-001", nombre="Sala Innovación",
                                  capacidad=10, tarifa_hora=50000)
    _reportar(gestor, r is not None, contadores)

    # ---- 5. Sala con capacidad negativa ------------------------------------
    print("\n[5] Creación de una sala con capacidad negativa")
    r = gestor.registrar_servicio(ReservaSala, identificador="S-099", nombre="Sala Defectuosa",
                                  capacidad=-5, tarifa_hora=40000)
    _reportar(gestor, r is not None, contadores)

    # ---- 6. Equipo válido --------------------------------------------------
    print("\n[6] Creación de un alquiler de equipo válido")
    r = gestor.registrar_servicio(AlquilerEquipo, identificador="S-002", nombre="Proyector HD",
                                  tarifa_dia=80000, deposito=100000)
    _reportar(gestor, r is not None, contadores)

    # ---- 7. Asesoría válida ------------------------------------------------
    print("\n[7] Creación de una asesoría especializada válida")
    r = gestor.registrar_servicio(AsesoriaEspecializada, identificador="S-003",
                                  nombre="Asesoría en Datos", tarifa_hora_base=120000,
                                  nivel="senior")
    _reportar(gestor, r is not None, contadores)

    # ---- 8. Reserva exitosa (crear, confirmar y procesar con IVA y descuento)
    print("\n[8] Reserva exitosa: 3 horas de sala, IVA 19 % y descuento 10 %")
    reserva = gestor.crear_reserva("R-001", "C-001", "S-001", 3)
    ok = reserva is not None
    if ok:
        ok = gestor.confirmar_reserva("R-001") is not None
    if ok:
        costo = gestor.procesar_reserva("R-001", impuesto=0.19, descuento=0.10)
        ok = costo is not None
        if ok:
            # Verificación manual: 150.000 x 0,90 x 1,19 = 160.650,00
            print(f"   Costo total calculado: ${costo:,.2f}")
    _reportar(gestor, ok, contadores)

    # ---- 9. Reserva de un servicio no disponible ---------------------------
    print("\n[9] Reserva de un servicio marcado como no disponible")
    gestor.registrar_servicio(AlquilerEquipo, identificador="S-004", nombre="Portátil Gamer",
                              tarifa_dia=90000, deposito=0, disponible=False)
    r = gestor.crear_reserva("R-002", "C-001", "S-004", 2)
    _reportar(gestor, r is not None, contadores)

    # ---- 10. Reserva con duración inválida (0 horas) -----------------------
    print("\n[10] Reserva con duración inválida (0 horas)")
    r = gestor.crear_reserva("R-003", "C-001", "S-001", 0)
    _reportar(gestor, r is not None, contadores)

    # ---- 11. Cancelar una reserva ya procesada -----------------------------
    print("\n[11] Cancelación de una reserva ya procesada (operación no permitida)")
    r = gestor.cancelar_reserva("R-001")
    _reportar(gestor, r is not None, contadores)

    # ---- 12. Procesar con descuento superior al 100 % ----------------------
    print("\n[12] Procesamiento con descuento del 150 % (cálculo inconsistente)")
    gestor.crear_reserva("R-004", "C-001", "S-002", 2)
    gestor.confirmar_reserva("R-004")
    r = gestor.procesar_reserva("R-004", impuesto=0.19, descuento=1.5)
    _reportar(gestor, r is not None, contadores)

    # ---- Resumen final -----------------------------------------------------
    print("\n" + "=" * 70)
    print(" RESUMEN FINAL")
    print("=" * 70)
    print(f" Operaciones simuladas : {contadores['exitosas'] + contadores['rechazadas']}")
    print(f" Exitosas              : {contadores['exitosas']}")
    print(f" Errores controlados   : {contadores['rechazadas']}")
    print(f" Estado del sistema    : {gestor.resumen()}")
    print(f" Archivo de registro   : {ARCHIVO_LOG}")
    print("\n Reservas registradas:")
    for reserva in gestor.reservas:
        print(f"   - {reserva.describir()}")
    _log.info("Simulación finalizada: %s exitosas, %s errores controlados",
              contadores["exitosas"], contadores["rechazadas"])

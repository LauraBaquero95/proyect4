# -*- coding: utf-8 -*-
"""
Módulo: gestor_fj.py
Propósito: coordinar clientes, servicios y reservas mediante LISTAS internas
           (sin base de datos) y garantizar que ningún error detenga el programa.

Justificación de diseño:
    Todas las operaciones públicas pasan por '_ejecutar_seguro()', un único punto
    donde se capturan, registran y neutralizan los errores. Esto asegura que la
    aplicación continúe activa y evita repetir bloques try/except en cada método.
"""

from src.excepciones.errores import (
    ClienteInvalidoError,
    ErrorSoftwareFJ,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioInvalidoError,
)
from src.modelos.cliente import Cliente
from src.modelos.reserva import Reserva
from src.modelos.servicio import Servicio
from src.utilidades.logger import describir_error, obtener_logger

_log = obtener_logger()


class GestorFJ:
    """Controlador central del sistema de Software FJ."""

    def __init__(self):
        # Listas privadas: son el "almacenamiento" del sistema (sin base de datos).
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        # Texto del último error ocurrido (None si la última operación fue exitosa).
        self.ultimo_error = None

    # -------- consulta de listas (se devuelven copias para proteger el estado) --------
    @property
    def clientes(self):
        return tuple(self.__clientes)

    @property
    def servicios(self):
        return tuple(self.__servicios)

    @property
    def reservas(self):
        return tuple(self.__reservas)

    # ----------------------- núcleo de manejo de errores -----------------------
    def _ejecutar_seguro(self, descripcion, accion):
        """
        Ejecuta 'accion' (una función sin argumentos) dentro de un bloque protegido.
        Devuelve el resultado si todo sale bien, o None si ocurre cualquier error.
        """
        self.ultimo_error = None
        try:
            resultado = accion()
        except ErrorSoftwareFJ as error:
            # Error PREVISTO por el sistema: se registra con su cadena de causas.
            self.ultimo_error = str(error)
            _log.error("%s rechazada | %s", descripcion, describir_error(error))
            return None
        except Exception as error:  # noqa: BLE001 - red de seguridad para errores imprevistos
            # Error NO previsto: se registra como crítico con traza completa y se continúa.
            self.ultimo_error = f"Error inesperado: {error}"
            _log.critical("%s | ERROR INESPERADO | %s", descripcion, describir_error(error), exc_info=True)
            return None
        else:
            _log.info("%s completada correctamente", descripcion)
            return resultado
        finally:
            _log.debug("Fin de la operación: %s", descripcion)

    # --------------------------- utilidades internas ---------------------------
    @staticmethod
    def _construir(clase, datos):
        """Crea un objeto; si faltan o sobran argumentos, lanza ParametroFaltanteError."""
        try:
            return clase(**datos)
        except TypeError as error:
            # TypeError aparece al faltar argumentos o al instanciar una clase abstracta.
            raise ParametroFaltanteError(
                f"Parámetros incorrectos o faltantes al crear {clase.__name__}: {error}"
            ) from error

    @staticmethod
    def _buscar(lista, identificador, clase_error, etiqueta):
        """Busca por identificador en una lista; si no existe, lanza la excepción indicada."""
        for elemento in lista:
            if elemento.identificador == identificador:
                return elemento
        raise clase_error(f"No existe {etiqueta} con identificador '{identificador}'.")

    @staticmethod
    def _verificar_duplicado(lista, identificador, clase_error, etiqueta):
        """Impide registrar dos elementos con el mismo identificador."""
        if any(elemento.identificador == identificador for elemento in lista):
            raise clase_error(f"Ya existe {etiqueta} con identificador '{identificador}'.")

    # ------------------------------ operaciones ------------------------------
    def registrar_cliente(self, **datos):
        """Crea y registra un cliente. Devuelve el Cliente o None si hubo error."""
        def accion():
            cliente = self._construir(Cliente, datos)
            self._verificar_duplicado(self.__clientes, cliente.identificador,
                                      ClienteInvalidoError, "un cliente")
            self.__clientes.append(cliente)
            return cliente
        return self._ejecutar_seguro("Registro de cliente", accion)

    def registrar_servicio(self, clase_servicio, **datos):
        """Crea y registra un servicio de cualquier clase hija de Servicio."""
        def accion():
            servicio = self._construir(clase_servicio, datos)
            self._verificar_duplicado(self.__servicios, servicio.identificador,
                                      ServicioInvalidoError, "un servicio")
            self.__servicios.append(servicio)
            return servicio
        return self._ejecutar_seguro(f"Registro de servicio ({clase_servicio.__name__})", accion)

    def crear_reserva(self, identificador, id_cliente, id_servicio, duracion):
        """Crea una reserva PENDIENTE. Devuelve la Reserva o None si hubo error."""
        def accion():
            cliente = self._buscar(self.__clientes, id_cliente, ClienteInvalidoError, "un cliente")
            servicio = self._buscar(self.__servicios, id_servicio, ReservaInvalidaError, "un servicio")
            self._verificar_duplicado(self.__reservas, identificador,
                                      ReservaInvalidaError, "una reserva")
            reserva = Reserva(identificador, cliente, servicio, duracion)
            self.__reservas.append(reserva)
            return reserva
        return self._ejecutar_seguro("Creación de reserva", accion)

    def confirmar_reserva(self, id_reserva):
        """Confirma una reserva. Devuelve True si tuvo éxito, None si falló."""
        def accion():
            self._buscar(self.__reservas, id_reserva, ReservaInvalidaError, "una reserva").confirmar()
            return True
        return self._ejecutar_seguro(f"Confirmación de reserva {id_reserva}", accion)

    def cancelar_reserva(self, id_reserva):
        """Cancela una reserva. Devuelve True si tuvo éxito, None si falló."""
        def accion():
            self._buscar(self.__reservas, id_reserva, ReservaInvalidaError, "una reserva").cancelar()
            return True
        return self._ejecutar_seguro(f"Cancelación de reserva {id_reserva}", accion)

    def procesar_reserva(self, id_reserva, impuesto=0.0, descuento=0.0):
        """Procesa una reserva. Devuelve el costo total o None si falló."""
        def accion():
            reserva = self._buscar(self.__reservas, id_reserva, ReservaInvalidaError, "una reserva")
            return reserva.procesar(impuesto, descuento)
        return self._ejecutar_seguro(f"Procesamiento de reserva {id_reserva}", accion)

    def buscar_reserva(self, id_reserva):
        """Devuelve la reserva con ese identificador, o None si no existe."""
        for reserva in self.__reservas:
            if reserva.identificador == id_reserva:
                return reserva
        return None

    def resumen(self):
        """Texto con el total de elementos registrados."""
        return (f"Clientes: {len(self.__clientes)} | Servicios: {len(self.__servicios)} "
                f"| Reservas: {len(self.__reservas)}")

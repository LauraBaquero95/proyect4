# -*- coding: utf-8 -*-
"""
Módulo: reserva.py
Propósito: integrar cliente, servicio, duración y estado en una reserva.

Ciclo de vida:
    PENDIENTE --confirmar()--> CONFIRMADA --procesar()--> PROCESADA
    PENDIENTE o CONFIRMADA --cancelar()--> CANCELADA
Cualquier transición distinta lanza OperacionNoPermitidaError.
"""

from enum import Enum

from src.excepciones.errores import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from src.modelos.cliente import Cliente
from src.modelos.entidad_base import EntidadBase
from src.modelos.servicio import Servicio
from src.utilidades.logger import obtener_logger

_log = obtener_logger()


class EstadoReserva(Enum):
    """Estados posibles. Un Enum evita escribir textos sueltos propensos a errores."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, identificador, cliente, servicio, duracion):
        # Se valida el identificador usando la clase padre.
        try:
            super().__init__(identificador)
        except ValueError as error:
            raise ReservaInvalidaError(f"Identificador de reserva inválido: {error}") from error

        # Se verifica el TIPO de los objetos recibidos (evita errores más adelante).
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        # No se puede reservar un servicio no disponible.
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible actualmente."
            )

        # Se convierte la duración a número; si no es posible, la reserva es inválida.
        try:
            duracion_numerica = float(duracion)
        except (TypeError, ValueError) as error:
            raise ReservaInvalidaError("La duración debe ser un valor numérico.") from error
        # La regla de rango la decide cada servicio (polimorfismo).
        servicio.validar_parametros(duracion_numerica)

        # Atributos privados: el estado solo cambia mediante los métodos de la clase.
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion_numerica
        self.__estado = EstadoReserva.PENDIENTE
        self.__costo_total = None  # Se calcula únicamente al procesar.

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    # ------------------------------ acciones ------------------------------
    def confirmar(self):
        """Pasa la reserva de PENDIENTE a CONFIRMADA."""
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"Solo se puede confirmar una reserva PENDIENTE (estado actual: {self.__estado.value})."
            )
        # Se vuelve a verificar la disponibilidad: pudo cambiar desde que se creó.
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.__servicio.nombre}' dejó de estar disponible."
            )
        self.__estado = EstadoReserva.CONFIRMADA

    def cancelar(self):
        """Cancela la reserva si aún no fue procesada ni cancelada."""
        if self.__estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self.__estado.value}."
            )
        self.__estado = EstadoReserva.CANCELADA

    def procesar(self, impuesto=0.0, descuento=0.0):
        """
        Procesa una reserva CONFIRMADA y calcula su costo total.
        Usa try/except/else/finally y encadenamiento de excepciones.
        """
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se puede procesar una reserva CONFIRMADA (estado actual: {self.__estado.value})."
            )
        try:
            # Intento de cálculo: puede fallar si impuesto/descuento son incoherentes.
            costo = self.__servicio.calcular_costo(self.__duracion, impuesto, descuento)
        except CalculoInconsistenteError as error:
            # Se registra y se relanza como otra excepción, CONSERVANDO la causa (from).
            _log.warning("Fallo de cálculo en reserva %s: %s", self.identificador, error)
            raise OperacionNoPermitidaError(
                f"No fue posible procesar la reserva {self.identificador}."
            ) from error
        else:
            # El bloque 'else' solo se ejecuta si NO hubo excepción: se confirma el cambio.
            self.__costo_total = costo
            self.__estado = EstadoReserva.PROCESADA
            return costo
        finally:
            # El bloque 'finally' se ejecuta SIEMPRE, haya o no error.
            _log.debug("Finalizó el intento de procesar la reserva %s", self.identificador)

    def describir(self):
        costo = f"${self.__costo_total:,.2f}" if self.__costo_total is not None else "sin calcular"
        return (f"Reserva {self.identificador} | {self.__cliente.nombre} -> {self.__servicio.nombre} "
                f"| duración {self.__duracion:g} | estado {self.__estado.value} | costo {costo}")

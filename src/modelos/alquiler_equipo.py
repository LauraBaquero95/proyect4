# -*- coding: utf-8 -*-
"""
Módulo: alquiler_equipo.py
Propósito: servicio especializado de alquiler de equipos (se cobra por día + depósito).
"""

from src.excepciones.errores import ServicioInvalidoError
from src.modelos.servicio import Servicio
from src.utilidades.validadores import validar_numero_positivo


class AlquilerEquipo(Servicio):
    """Equipo con tarifa diaria y depósito de garantía."""

    def __init__(self, identificador, nombre, tarifa_dia, deposito, disponible=True):
        super().__init__(identificador, nombre, disponible)
        try:
            self._tarifa_dia = validar_numero_positivo(tarifa_dia, "tarifa por día")
            # El depósito puede ser cero (equipos sin garantía), por eso permitir_cero=True.
            self._deposito = validar_numero_positivo(deposito, "depósito", permitir_cero=True)
        except ValueError as error:
            raise ServicioInvalidoError(f"Datos de equipo inválidos: {error}") from error

    # Método SOBRESCRITO: tarifa por días + depósito de garantía.
    def _costo_base(self, duracion):
        return self._tarifa_dia * duracion + self._deposito

    # Método SOBRESCRITO: un equipo se alquila de 1 a 30 días.
    def validar_parametros(self, duracion):
        self._validar_rango_duracion(duracion, 1, 30, "días")

    def describir(self):
        return (f"Equipo '{self.nombre}' ({self.identificador}) | ${self._tarifa_dia:,.2f} por día "
                f"| depósito ${self._deposito:,.2f}")

# -*- coding: utf-8 -*-
"""
Módulo: reserva_sala.py
Propósito: servicio especializado de reserva de salas (se cobra por hora).
"""

from src.excepciones.errores import ServicioInvalidoError
from src.modelos.servicio import Servicio
from src.utilidades.validadores import validar_numero_positivo


class ReservaSala(Servicio):
    """Sala de reuniones con capacidad y tarifa por hora."""

    def __init__(self, identificador, nombre, capacidad, tarifa_hora, disponible=True):
        # Se inicializa la parte común (id, nombre, disponibilidad) en la clase padre.
        super().__init__(identificador, nombre, disponible)
        try:
            self._capacidad = validar_numero_positivo(capacidad, "capacidad", entero=True)
            self._tarifa_hora = validar_numero_positivo(tarifa_hora, "tarifa por hora")
        except ValueError as error:
            raise ServicioInvalidoError(f"Datos de sala inválidos: {error}") from error

    @property
    def capacidad(self):
        return self._capacidad

    # Método SOBRESCRITO: la sala cobra tarifa por cantidad de horas.
    def _costo_base(self, duracion):
        return self._tarifa_hora * duracion

    # Método SOBRESCRITO: una sala se puede reservar de 1 a 12 horas.
    def validar_parametros(self, duracion):
        self._validar_rango_duracion(duracion, 1, 12, "horas")

    def describir(self):
        return (f"Sala '{self.nombre}' ({self.identificador}) | capacidad {self.capacidad} personas "
                f"| ${self._tarifa_hora:,.2f} por hora")

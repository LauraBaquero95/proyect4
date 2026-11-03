# -*- coding: utf-8 -*-
"""
Módulo: asesoria.py
Propósito: servicio especializado de asesorías (tarifa por hora según el nivel del asesor).
"""

from src.excepciones.errores import ServicioInvalidoError
from src.modelos.servicio import Servicio
from src.utilidades.validadores import validar_numero_positivo


class AsesoriaEspecializada(Servicio):
    """Asesoría cuyo precio por hora depende del nivel del asesor."""

    # Multiplicadores por nivel. Es un atributo de CLASE: se comparte entre instancias.
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, identificador, nombre, tarifa_hora_base, nivel="junior", disponible=True):
        super().__init__(identificador, nombre, disponible)
        try:
            self._tarifa_hora_base = validar_numero_positivo(tarifa_hora_base, "tarifa base por hora")
        except ValueError as error:
            raise ServicioInvalidoError(f"Datos de asesoría inválidos: {error}") from error
        nivel_normalizado = str(nivel).strip().lower()
        if nivel_normalizado not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' no válido. Opciones: {', '.join(self.NIVELES)}."
            )
        self._nivel = nivel_normalizado

    @property
    def nivel(self):
        return self._nivel

    # Método SOBRESCRITO: tarifa base x multiplicador del nivel x horas.
    def _costo_base(self, duracion):
        return self._tarifa_hora_base * self.NIVELES[self._nivel] * duracion

    # Método SOBRESCRITO: una asesoría dura de 1 a 8 horas.
    def validar_parametros(self, duracion):
        self._validar_rango_duracion(duracion, 1, 8, "horas")

    def describir(self):
        return (f"Asesoría '{self.nombre}' ({self.identificador}) | nivel {self.nivel} "
                f"| ${self._tarifa_hora_base * self.NIVELES[self._nivel]:,.2f} por hora")

# -*- coding: utf-8 -*-
"""
Módulo: servicio.py
Propósito: clase abstracta Servicio, base de todos los servicios de Software FJ.

Justificación de diseño (ver observación del tutor sobre código repetido):
    El cálculo con impuestos y descuentos se implementa UNA sola vez aquí, en
    'calcular_costo()'. Las clases hijas solo implementan '_costo_base()', que es
    lo que realmente cambia entre servicios. Así no se repite la lógica de
    porcentajes en cada hija y todas reutilizan el cálculo del padre.
"""

from abc import abstractmethod

from src.excepciones.errores import (
    CalculoInconsistenteError,
    ReservaInvalidaError,
    ServicioInvalidoError,
)
from src.modelos.entidad_base import EntidadBase
from src.utilidades.validadores import validar_texto


class Servicio(EntidadBase):
    """Clase abstracta: define qué debe saber hacer cualquier servicio."""

    def __init__(self, identificador, nombre, disponible=True):
        try:
            super().__init__(identificador)
            self._nombre = validar_texto(nombre, "nombre del servicio", minimo=3)
        except ValueError as error:
            raise ServicioInvalidoError(f"Datos de servicio inválidos: {error}") from error
        # Se fuerza a booleano para evitar valores ambiguos.
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        # Cambiar la disponibilidad es una operación controlada, no un atributo libre.
        self._disponible = bool(valor)

    # ------------------- métodos abstractos (contrato) -------------------
    @abstractmethod
    def _costo_base(self, duracion):
        """Costo sin impuestos ni descuentos. Lo define cada servicio especializado."""

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida que la duración sea coherente con las reglas del servicio."""

    # ------------- método con SOBRECARGA (parámetros opcionales) -------------
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        """
        Calcula el costo total. Python no tiene sobrecarga nativa; se simula con
        parámetros opcionales, lo que habilita tres variantes de llamada:

            servicio.calcular_costo(3)              -> costo base
            servicio.calcular_costo(3, 0.19)        -> con impuesto (IVA 19 %)
            servicio.calcular_costo(3, 0.19, 0.10)  -> con impuesto y descuento 10 %

        Orden de cálculo: primero se descuenta sobre el costo base y luego se
        aplica el impuesto sobre el valor ya descontado.
        """
        # 1) Se valida la duración con las reglas del servicio concreto (polimorfismo).
        self.validar_parametros(duracion)

        # 2) Se convierten los porcentajes a número; si no se puede, es un cálculo inválido.
        try:
            impuesto = float(impuesto)
            descuento = float(descuento)
        except (TypeError, ValueError) as error:
            raise CalculoInconsistenteError(
                "El impuesto y el descuento deben ser valores numéricos."
            ) from error

        # 3) Reglas de coherencia: impuesto entre 0 y 1; descuento menor que 1 (100 %).
        if not 0.0 <= impuesto <= 1.0:
            raise CalculoInconsistenteError(
                f"El impuesto debe estar entre 0 y 1 (recibido: {impuesto})."
            )
        if not 0.0 <= descuento < 1.0:
            raise CalculoInconsistenteError(
                f"El descuento debe ser mayor o igual a 0 y menor que 1 (recibido: {descuento})."
            )

        # 4) Cálculo: base -> descuento -> impuesto (cada servicio aporta solo la base).
        base = self._costo_base(duracion)
        total = base * (1.0 - descuento) * (1.0 + impuesto)

        # 5) Verificación defensiva: un costo no positivo indica una inconsistencia.
        if total <= 0:
            raise CalculoInconsistenteError(f"El costo calculado no es válido ({total}).")
        return round(total, 2)  # Se redondea a dos decimales (precisión monetaria).

    # ------------------- utilidad compartida por las hijas -------------------
    @staticmethod
    def _validar_rango_duracion(duracion, minimo, maximo, unidad):
        """Verifica que la duración esté entre un mínimo y un máximo permitidos."""
        if not minimo <= duracion <= maximo:
            raise ReservaInvalidaError(
                f"La duración debe estar entre {minimo} y {maximo} {unidad} (recibido: {duracion})."
            )

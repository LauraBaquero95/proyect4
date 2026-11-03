# -*- coding: utf-8 -*-
"""
Módulo: cliente.py
Propósito: representar a un cliente de Software FJ con datos personales protegidos.

Justificación de diseño:
    Los datos personales se guardan en atributos PRIVADOS (doble guion bajo) y se
    exponen solo mediante propiedades con validación. Así es imposible dejar al
    cliente en un estado inválido, ni siquiera después de creado (ENCAPSULACIÓN).
"""

from src.excepciones.errores import ClienteInvalidoError
from src.modelos.entidad_base import EntidadBase
from src.utilidades.validadores import (
    validar_correo,
    validar_nombre_persona,
    validar_telefono,
)


class Cliente(EntidadBase):
    """Cliente con validaciones robustas y datos personales encapsulados."""

    def __init__(self, identificador, nombre, correo, telefono):
        try:
            super().__init__(identificador)
        except ValueError as error:
            # Se traduce el error genérico a uno propio, conservando la causa.
            raise ClienteInvalidoError(f"Identificador de cliente inválido: {error}") from error
        # Se asigna mediante las propiedades para que SIEMPRE pasen por validación.
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    # ---------------------------- nombre ----------------------------
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        try:
            self.__nombre = validar_nombre_persona(valor)
        except ValueError as error:
            raise ClienteInvalidoError(f"Nombre inválido: {error}") from error

    # ---------------------------- correo ----------------------------
    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        try:
            self.__correo = validar_correo(valor)
        except ValueError as error:
            raise ClienteInvalidoError(f"Correo inválido: {error}") from error

    # --------------------------- teléfono ---------------------------
    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        try:
            self.__telefono = validar_telefono(valor)
        except ValueError as error:
            raise ClienteInvalidoError(f"Teléfono inválido: {error}") from error

    def describir(self):
        """Implementación del método abstracto de EntidadBase."""
        return f"Cliente {self.identificador}: {self.nombre} | {self.correo} | Tel. {self.telefono}"

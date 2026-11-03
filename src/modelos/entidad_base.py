# -*- coding: utf-8 -*-
"""
Módulo: entidad_base.py
Propósito: clase abstracta que representa cualquier entidad general del sistema.

Justificación de diseño:
    Cliente, Servicio y Reserva comparten un identificador y la obligación de
    describirse. Una clase abstracta (ABC) impone ese contrato: no se puede
    instanciar directamente y obliga a las hijas a implementar 'describir()'.
    Esto materializa los principios de ABSTRACCIÓN y POLIMORFISMO.
"""

from abc import ABC, abstractmethod

from src.utilidades.validadores import validar_texto


class EntidadBase(ABC):
    """Clase abstracta para todas las entidades del sistema."""

    def __init__(self, identificador):
        # Se valida el identificador (lanza ParametroFaltanteError o ValueError).
        # Atributo con guion bajo: es de uso interno (ENCAPSULACIÓN).
        self._identificador = validar_texto(identificador, "identificador", minimo=1)

    @property
    def identificador(self):
        """Solo lectura: una vez creada, la entidad no cambia de identificador."""
        return self._identificador

    @abstractmethod
    def describir(self):
        """Devuelve un texto descriptivo. Cada clase hija lo implementa a su manera."""

    def __str__(self):
        # Al imprimir cualquier entidad se usa su descripción (polimorfismo).
        return self.describir()

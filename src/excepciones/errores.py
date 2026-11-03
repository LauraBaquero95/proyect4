# -*- coding: utf-8 -*-
"""
Módulo: errores.py
Propósito: definir la jerarquía de excepciones personalizadas de Software FJ.

Justificación de diseño:
    Se crea una excepción base (ErrorSoftwareFJ) de la cual heredan todas las demás.
    Así, el sistema puede capturar CUALQUIER error propio con un solo
    'except ErrorSoftwareFJ', o bien un error específico cuando se requiera
    un tratamiento diferenciado. Cada excepción lleva un código único que
    facilita su búsqueda en el archivo de logs.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de la que heredan todas las excepciones del sistema."""

    def __init__(self, mensaje, codigo="FJ-000"):
        # Se delega el mensaje a Exception para conservar el comportamiento estándar.
        super().__init__(mensaje)
        # Se guarda el mensaje limpio (sin código) para poder mostrarlo al usuario.
        self.mensaje = mensaje
        # Se guarda el código identificador del tipo de error.
        self.codigo = codigo

    def __str__(self):
        # Formato uniforme: [CÓDIGO] mensaje. Es el que aparecerá en consola y en el log.
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los datos de un cliente son inválidos, duplicados o inexistentes."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-101")


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio se intenta crear con parámetros inválidos."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-102")


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta reservar un servicio que no está disponible."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-103")


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un parámetro obligatorio al crear u operar un objeto."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-104")


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta una acción que el estado actual no permite."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-105")


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza cuando una reserva tiene datos incorrectos (duración, cliente, servicio)."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-106")


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce o recibe valores incoherentes."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "FJ-107")

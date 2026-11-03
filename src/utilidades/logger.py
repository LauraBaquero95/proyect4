# -*- coding: utf-8 -*-
"""
Módulo: logger.py
Propósito: configurar el registro de eventos y errores en el archivo logs/eventos.log.

Justificación de diseño:
    La consigna permite el uso de archivos ÚNICAMENTE para registrar eventos y errores.
    Se usa el módulo estándar 'logging' porque agrega fecha, nivel y módulo de forma
    automática, y evita escribir manualmente en el archivo.
"""

import logging
from pathlib import Path

# Se calcula la raíz del proyecto subiendo dos niveles desde este archivo
# (utilidades -> src -> raíz). Así el log queda siempre en la misma carpeta,
# sin importar desde dónde se ejecute el programa.
RUTA_RAIZ = Path(__file__).resolve().parents[2]
RUTA_LOGS = RUTA_RAIZ / "logs"
ARCHIVO_LOG = RUTA_LOGS / "eventos.log"

# Nombre único del logger del sistema.
_NOMBRE_LOGGER = "software_fj"


def obtener_logger():
    """Devuelve el logger del sistema, configurándolo solo la primera vez."""
    logger = logging.getLogger(_NOMBRE_LOGGER)

    # Si ya tiene manejadores, ya fue configurado: se evita duplicar líneas en el log.
    if not logger.handlers:
        # Se crea la carpeta logs/ si no existe (exist_ok evita error si ya existe).
        RUTA_LOGS.mkdir(parents=True, exist_ok=True)
        # DEBUG captura todos los niveles (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        logger.setLevel(logging.DEBUG)
        # Modo "a" (append): cada ejecución agrega líneas sin borrar las anteriores.
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
        # Formato: fecha y hora | nivel | módulo que registró | mensaje.
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(module)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        manejador.setFormatter(formato)
        logger.addHandler(manejador)
        # Evita que los mensajes se propaguen al logger raíz y se impriman dos veces.
        logger.propagate = False
    return logger


def describir_error(error):
    """
    Construye un texto con el error y, si existe, su causa original.

    Cuando se usa 'raise NuevoError(...) from error_original', Python guarda el
    error original en el atributo __cause__. Aquí se aprovecha para dejar en el
    log TODA la cadena (encadenamiento de excepciones).
    """
    texto = f"{type(error).__name__}: {error}"
    causa = error.__cause__
    if causa is not None:
        texto += f" | causa original -> {type(causa).__name__}: {causa}"
    return texto

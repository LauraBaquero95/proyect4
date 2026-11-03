# -*- coding: utf-8 -*-
"""
Módulo: validadores.py
Propósito: funciones reutilizables de validación estricta.

Justificación de diseño:
    Centralizar las validaciones evita repetir código en cada clase (principio DRY)
    y garantiza que todas las reglas se apliquen de forma consistente.

Convención de errores:
    - Dato AUSENTE (None o vacío)  -> ParametroFaltanteError.
    - Dato PRESENTE pero incorrecto -> ValueError. La clase que invoca lo captura y
      lo convierte en una excepción propia con 'raise ... from', lo que demuestra
      el encadenamiento de excepciones.
"""

import re

from src.excepciones.errores import ParametroFaltanteError

# Patrón de correo: texto, arroba, dominio y al menos un punto con extensión.
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
# Patrón de teléfono: solo dígitos, entre 7 y 10 (fijo o celular colombiano).
_PATRON_TELEFONO = re.compile(r"^\d{7,10}$")


def validar_texto(valor, campo, minimo=2):
    """Valida que el valor sea un texto no vacío con una longitud mínima."""
    # Caso 1: el parámetro no llegó o llegó vacío -> parámetro faltante.
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
    # Caso 2: llegó algo que no es texto (por ejemplo, un número).
    if not isinstance(valor, str):
        raise ValueError(f"El campo '{campo}' debe ser texto.")
    limpio = valor.strip()  # Se eliminan espacios sobrantes al inicio y al final.
    if len(limpio) < minimo:
        raise ValueError(f"El campo '{campo}' debe tener al menos {minimo} caracteres.")
    return limpio


def validar_nombre_persona(valor):
    """Valida un nombre: solo letras, espacios y signos habituales (' - .)."""
    limpio = validar_texto(valor, "nombre", minimo=3)
    # Se recorre cada carácter para rechazar dígitos y símbolos extraños.
    if not all(c.isalpha() or c.isspace() or c in "'-." for c in limpio):
        raise ValueError("El nombre solo puede contener letras y espacios.")
    return limpio


def validar_correo(valor):
    """Valida el formato de un correo electrónico."""
    limpio = validar_texto(valor, "correo", minimo=5)
    if not _PATRON_CORREO.match(limpio):
        raise ValueError(f"El correo '{limpio}' no tiene un formato válido.")
    return limpio.lower()  # Se normaliza a minúsculas para evitar duplicados.


def validar_telefono(valor):
    """Valida un teléfono de 7 a 10 dígitos (se permiten espacios que se eliminan)."""
    limpio = validar_texto(valor, "teléfono", minimo=7).replace(" ", "")
    if not _PATRON_TELEFONO.match(limpio):
        raise ValueError("El teléfono debe tener entre 7 y 10 dígitos numéricos.")
    return limpio


def validar_numero_positivo(valor, campo, entero=False, permitir_cero=False):
    """
    Valida que el valor sea numérico y positivo.

    Parámetros:
        entero        -> si es True, exige un número entero (por ejemplo, capacidad).
        permitir_cero -> si es True, acepta 0 (por ejemplo, un depósito en cero).
    """
    if valor is None:
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
    # En Python, True y False son enteros; se rechazan para evitar datos absurdos.
    if isinstance(valor, bool):
        raise ValueError(f"El campo '{campo}' debe ser numérico.")
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        # Se encadena el error original para no perder la causa real.
        raise ValueError(f"El campo '{campo}' debe ser numérico.") from error
    if entero and numero != int(numero):
        raise ValueError(f"El campo '{campo}' debe ser un número entero.")
    if numero < 0 or (numero == 0 and not permitir_cero):
        raise ValueError(f"El campo '{campo}' debe ser mayor que cero.")
    return int(numero) if entero else numero

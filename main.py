# -*- coding: utf-8 -*-
"""
Archivo: main.py
Propósito: punto de entrada del sistema. Solo arranca la simulación; no contiene
           lógica de negocio (separación de responsabilidades).

Ejecución:  python main.py
"""

import sys

from simulacion.operaciones import ejecutar_simulacion
from src.gestion.gestor_fj import GestorFJ
from src.utilidades.logger import obtener_logger


def main():
    # Se fuerza UTF-8 en la consola para mostrar tildes correctamente (sobre todo en Windows).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    log = obtener_logger()
    log.info("=== INICIO DE EJECUCIÓN DE SOFTWARE FJ ===")
    try:
        gestor = GestorFJ()
        ejecutar_simulacion(gestor)
    except Exception as error:  # noqa: BLE001 - última barrera de seguridad
        # Aun un fallo gravísimo queda registrado y se informa de forma controlada.
        log.critical("Fallo no controlado en main: %s", error, exc_info=True)
        print(f"Se produjo un error crítico: {error}. Revise logs/eventos.log")
    finally:
        log.info("=== FIN DE EJECUCIÓN ===")


if __name__ == "__main__":
    main()

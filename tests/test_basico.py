# -*- coding: utf-8 -*-
"""
Pruebas básicas con 'unittest' (biblioteca estándar, no requiere instalar nada).
Ejecución: python -m unittest discover -s tests -t .
"""

import unittest

from src.excepciones.errores import (
    CalculoInconsistenteError,
    ClienteInvalidoError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
)
from src.modelos.cliente import Cliente
from src.modelos.reserva import Reserva
from src.modelos.reserva_sala import ReservaSala


class PruebasSoftwareFJ(unittest.TestCase):

    def setUp(self):
        # Se crean objetos válidos que se reutilizan en cada prueba.
        self.cliente = Cliente("C-T1", "Ana Pérez", "ana@correo.com", "3001234567")
        self.sala = ReservaSala("S-T1", "Sala Test", 8, 50000)

    def test_cliente_correo_invalido(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("C-T2", "Luis Mora", "correo-malo", "3001234567")

    def test_costo_con_impuesto_y_descuento(self):
        # 3 h x 50.000 = 150.000 -> x 0,90 = 135.000 -> x 1,19 = 160.650
        self.assertEqual(self.sala.calcular_costo(3, 0.19, 0.10), 160650.0)

    def test_costo_base_sin_extras(self):
        self.assertEqual(self.sala.calcular_costo(2), 100000.0)

    def test_descuento_excesivo(self):
        with self.assertRaises(CalculoInconsistenteError):
            self.sala.calcular_costo(3, 0.19, 1.5)

    def test_cancelar_reserva_procesada(self):
        reserva = Reserva("R-T1", self.cliente, self.sala, 2)
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar()

    def test_servicio_no_disponible(self):
        self.sala.disponible = False
        with self.assertRaises(ServicioNoDisponibleError):
            Reserva("R-T2", self.cliente, self.sala, 2)


if __name__ == "__main__":
    unittest.main()

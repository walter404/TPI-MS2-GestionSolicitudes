"""Prueba de caracterizacion: la version 1 y la version 2 deben comportarse igual.

Se ejecuta la misma secuencia de operaciones sobre ambas versiones, cada una con
su propio archivo, y se comparan en cada paso: valor devuelto, texto impreso y
contenido final del archivo JSON.
"""
import contextlib
import io
import json
import os
import tempfile
import unittest

from legacy.gestor_solicitudes_v1 import GestorSolicitudesSistema
from solicitudes import GestorSolicitudesConsola

PASOS = [
    ("crear valida", "CREAR", dict(dni="30111222", nombre="Estudiante Demo 1",
                                   tipo="Equivalencia", desc="Pedido de pase")),
    ("crear segunda", "CREAR", dict(dni="31222333", nombre="Estudiante Demo 2",
                                    tipo="Reclamo", desc="Reclamo de nota")),
    ("crear dni corto", "CREAR", dict(dni="123", nombre="Demo", tipo="Reclamo", desc="x")),
    ("crear dni vacio", "CREAR", dict(dni="", nombre="Demo", tipo="Reclamo", desc="x")),
    ("crear sin dni", "CREAR", dict(nombre="Demo", tipo="Reclamo", desc="x")),
    ("crear tipo vacio", "CREAR", dict(dni="30111222", nombre="Demo", tipo="", desc="x")),
    ("crear dni de 7", "CREAR", dict(dni="1234567", nombre="Demo 3", tipo="Excepcion",
                                     desc="limite")),
    ("crear sin nombre", "CREAR", dict(dni="40111222", tipo="Reclamo")),
    ("estado valido", "CAMBIAR_ESTADO", dict(id_sol=1, estado="EN_PROCESO")),
    ("estado resuelto", "CAMBIAR_ESTADO", dict(id_sol=2, estado="RESUELTO")),
    ("estado invalido", "CAMBIAR_ESTADO", dict(id_sol=1, estado="ARCHIVADO")),
    ("estado nulo", "CAMBIAR_ESTADO", dict(id_sol=1)),
    ("estado en minusculas", "CAMBIAR_ESTADO", dict(id_sol=1, estado="resuelto")),
    ("estado id inexistente", "CAMBIAR_ESTADO", dict(id_sol=99, estado="RESUELTO")),
    ("estado invalido e id inexistente", "CAMBIAR_ESTADO", dict(id_sol=99, estado="X")),
    ("asignar valido", "ASIGNAR", dict(id_sol=1, resp="Area Alumnos")),
    ("asignar sin responsable", "ASIGNAR", dict(id_sol=3)),
    ("asignar id inexistente", "ASIGNAR", dict(id_sol=99, resp="Area Alumnos")),
    ("filtrar por dni", "FILTRAR", dict(dni="30111222")),
    ("filtrar por estado", "FILTRAR", dict(estado="RESUELTO")),
    ("filtrar por dni y estado", "FILTRAR", dict(dni="30111222", estado="RESUELTO")),
    ("filtrar sin criterios", "FILTRAR", dict()),
    ("filtrar sin coincidencias", "FILTRAR", dict(dni="99999999")),
    ("reporte", "REPORTE", dict()),
    ("operacion desconocida", "BORRAR", dict(id_sol=1)),
]


def ejecutar(gestor, op, kwargs):
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        devuelto = gestor.ejecutar_operacion(op, **kwargs)
    return devuelto, salida.getvalue()


def leer(archivo):
    with open(archivo, encoding="utf-8") as f:
        return json.load(f)


class TestEquivalenciaV1V2(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.archivo_v1 = os.path.join(carpeta.name, "v1.json")
        self.archivo_v2 = os.path.join(carpeta.name, "v2.json")
        self.v1 = GestorSolicitudesSistema(self.archivo_v1)
        self.v2 = GestorSolicitudesConsola(self.archivo_v2)

    def test_misma_secuencia_mismo_comportamiento(self):
        for nombre, op, kwargs in PASOS:
            with self.subTest(paso=nombre):
                devuelto_1, texto_1 = ejecutar(self.v1, op, kwargs)
                devuelto_2, texto_2 = ejecutar(self.v2, op, kwargs)
                self.assertEqual(devuelto_1, devuelto_2, "valor devuelto distinto")
                self.assertEqual(texto_1, texto_2, "mensajes impresos distintos")
                self.assertEqual(leer(self.archivo_v1), leer(self.archivo_v2),
                                 "contenido del archivo distinto")

    def test_los_archivos_generados_son_identicos_byte_a_byte(self):
        for _nombre, op, kwargs in PASOS:
            ejecutar(self.v1, op, kwargs)
            ejecutar(self.v2, op, kwargs)
        with open(self.archivo_v1, "rb") as f1, open(self.archivo_v2, "rb") as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_la_secuencia_cubre_las_cinco_operaciones(self):
        self.assertEqual({op for _n, op, _k in PASOS},
                         {"CREAR", "CAMBIAR_ESTADO", "ASIGNAR", "FILTRAR", "REPORTE",
                          "BORRAR"})


if __name__ == "__main__":
    unittest.main()

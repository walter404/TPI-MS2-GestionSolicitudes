"""Casos donde la version 2 mejora deliberadamente a la version 1 (ante archivo danado)."""
import contextlib
import io
import os
import tempfile
import unittest

from solicitudes import GestorSolicitudesConsola


class TestConsolaConArchivoDanado(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.archivo = os.path.join(carpeta.name, "solicitudes.json")
        self.gestor = GestorSolicitudesConsola(self.archivo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.gestor.ejecutar_operacion("CREAR", dni="30111222", nombre="Demo",
                                           tipo="Reclamo", desc="x")
        with open(self.archivo, "w", encoding="utf-8") as f:
            f.write("{danado")

    def ejecutar(self, op, **kwargs):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            devuelto = self.gestor.ejecutar_operacion(op, **kwargs)
        return devuelto, salida.getvalue()

    def test_no_se_cae_y_avisa(self):
        devuelto, texto = self.ejecutar("REPORTE")
        self.assertIsNone(devuelto)
        self.assertIn("no se pudo acceder", texto)

    def test_crear_no_sobrescribe_el_archivo_danado(self):
        self.ejecutar("CREAR", dni="30111222", nombre="Demo", tipo="Reclamo", desc="x")
        with open(self.archivo, encoding="utf-8") as f:
            self.assertEqual(f.read(), "{danado")


if __name__ == "__main__":
    unittest.main()

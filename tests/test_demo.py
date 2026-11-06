import contextlib
import io
import unittest

from solicitudes.__main__ import main


class TestDemo(unittest.TestCase):
    def test_la_demo_corre_y_muestra_el_reporte(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            main()
        texto = salida.getvalue()
        self.assertIn("Solicitud creada con exito.", texto)
        self.assertIn("Error: Datos invalidos.", texto)
        self.assertIn("Total: 1 | Pendientes: 0 | Resueltos: 1", texto)


if __name__ == "__main__":
    unittest.main()

import unittest

from solicitudes import (DatosInvalidosError, DatosNuevaSolicitud,
                         EstadoInvalidoError, EstadoSolicitud, Estudiante,
                         Solicitud)


class TestEstadoSolicitud(unittest.TestCase):
    def test_desde_texto_valido(self):
        self.assertIs(EstadoSolicitud.desde_texto("RESUELTO"), EstadoSolicitud.RESUELTO)

    def test_desde_texto_acepta_estado_ya_tipado(self):
        self.assertIs(EstadoSolicitud.desde_texto(EstadoSolicitud.RECHAZADO),
                      EstadoSolicitud.RECHAZADO)

    def test_desde_texto_invalido_lanza_excepcion(self):
        for valor in ("ARCHIVADO", "", None, "resuelto"):
            with self.subTest(valor=valor):
                with self.assertRaises(EstadoInvalidoError):
                    EstadoSolicitud.desde_texto(valor)


class TestDatosNuevaSolicitud(unittest.TestCase):
    def test_datos_validos(self):
        DatosNuevaSolicitud("30111222", "Estudiante Demo", "Reclamo", "Desc").validar()

    def test_dni_exactamente_siete_caracteres_es_valido(self):
        DatosNuevaSolicitud("1234567", "Estudiante Demo", "Reclamo", "Desc").validar()

    def test_dni_corto_es_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            DatosNuevaSolicitud("123456", "Estudiante Demo", "Reclamo", "Desc").validar()

    def test_dni_vacio_o_nulo_es_invalido(self):
        for dni in ("", None):
            with self.subTest(dni=dni):
                with self.assertRaises(DatosInvalidosError):
                    DatosNuevaSolicitud(dni, "Estudiante Demo", "Reclamo", "Desc").validar()

    def test_tipo_vacio_o_nulo_es_invalido(self):
        for tipo in ("", None):
            with self.subTest(tipo=tipo):
                with self.assertRaises(DatosInvalidosError):
                    DatosNuevaSolicitud("30111222", "Estudiante Demo", tipo, "Desc").validar()


class TestSolicitud(unittest.TestCase):
    def setUp(self):
        self.solicitud = Solicitud(1, Estudiante("30111222", "Estudiante Demo"),
                                   "Reclamo", "Desc", "2026-11-05")

    def test_valores_iniciales(self):
        self.assertIs(self.solicitud.estado, EstadoSolicitud.PENDIENTE)
        self.assertEqual(self.solicitud.responsable.nombre, "SIN ASIGNAR")

    def test_cambiar_estado_acepta_texto(self):
        self.solicitud.cambiar_estado("EN_PROCESO")
        self.assertIs(self.solicitud.estado, EstadoSolicitud.EN_PROCESO)

    def test_asignar_responsable(self):
        self.solicitud.asignar_a("Area Alumnos")
        self.assertEqual(self.solicitud.responsable.nombre, "Area Alumnos")


if __name__ == "__main__":
    unittest.main()

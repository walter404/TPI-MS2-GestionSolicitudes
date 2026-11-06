import unittest
from datetime import date

from solicitudes import (ConsultaService, DatosInvalidosError, DatosNuevaSolicitud,
                         EstadoInvalidoError, EstadoSolicitud, RepositorioEnMemoria,
                         SolicitudNoEncontradaError, SolicitudService)


def datos(dni="30111222", nombre="Estudiante Demo", tipo="Equivalencia", desc="Pase"):
    return DatosNuevaSolicitud(dni, nombre, tipo, desc)


class BaseServicios(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioEnMemoria()
        self.comandos = SolicitudService(self.repo, hoy=lambda: date(2026, 11, 5))
        self.consultas = ConsultaService(self.repo)


class TestCrearSolicitud(BaseServicios):
    def test_crear_solicitud_valida(self):
        sol = self.comandos.crear_solicitud(datos())
        self.assertEqual(sol.id, 1)
        self.assertEqual(sol.estado, EstadoSolicitud.PENDIENTE)
        self.assertEqual(sol.responsable.nombre, "SIN ASIGNAR")
        self.assertEqual(sol.fecha, "2026-11-05")

    def test_ids_consecutivos(self):
        ids = [self.comandos.crear_solicitud(datos()).id for _ in range(3)]
        self.assertEqual(ids, [1, 2, 3])

    def test_dni_invalido_lanza_excepcion_y_no_persiste(self):
        with self.assertRaises(DatosInvalidosError):
            self.comandos.crear_solicitud(datos(dni="123"))
        self.assertEqual(self.repo.obtener_todas(), [])

    def test_tipo_vacio_lanza_excepcion(self):
        with self.assertRaises(DatosInvalidosError):
            self.comandos.crear_solicitud(datos(tipo=""))


class TestCambiarEstadoYAsignar(BaseServicios):
    def setUp(self):
        super().setUp()
        self.sol = self.comandos.crear_solicitud(datos())

    def test_cambiar_estado_persiste(self):
        self.comandos.cambiar_estado(self.sol.id, "EN_PROCESO")
        self.assertEqual(self.repo.obtener_todas()[0].estado, EstadoSolicitud.EN_PROCESO)

    def test_cambiar_estado_invalido_no_modifica(self):
        with self.assertRaises(EstadoInvalidoError):
            self.comandos.cambiar_estado(self.sol.id, "ARCHIVADO")
        self.assertEqual(self.repo.obtener_todas()[0].estado, EstadoSolicitud.PENDIENTE)

    def test_cambiar_estado_id_inexistente(self):
        with self.assertRaises(SolicitudNoEncontradaError):
            self.comandos.cambiar_estado(99, "RESUELTO")

    def test_id_inexistente_tiene_prioridad_sobre_estado_invalido(self):
        # Orden de validacion heredado de la version 1.
        with self.assertRaises(SolicitudNoEncontradaError):
            self.comandos.cambiar_estado(99, "ARCHIVADO")

    def test_asignar_responsable_persiste(self):
        self.comandos.asignar_responsable(self.sol.id, "Area Alumnos")
        self.assertEqual(self.repo.obtener_todas()[0].responsable.nombre, "Area Alumnos")

    def test_asignar_id_inexistente(self):
        with self.assertRaises(SolicitudNoEncontradaError):
            self.comandos.asignar_responsable(99, "Area Alumnos")


class TestConsultas(BaseServicios):
    def setUp(self):
        super().setUp()
        self.s1 = self.comandos.crear_solicitud(datos(dni="30111222"))
        self.s2 = self.comandos.crear_solicitud(datos(dni="31222333"))
        self.comandos.cambiar_estado(self.s2.id, "RESUELTO")

    def test_filtrar_por_estado(self):
        encontradas = self.consultas.filtrar(estado=EstadoSolicitud.RESUELTO)
        self.assertEqual([s.id for s in encontradas], [self.s2.id])

    def test_filtrar_por_estado_como_texto(self):
        self.assertEqual(len(self.consultas.filtrar(estado="PENDIENTE")), 1)

    def test_filtrar_por_dni(self):
        encontradas = self.consultas.filtrar(dni="30111222")
        self.assertEqual([s.id for s in encontradas], [self.s1.id])

    def test_filtrar_sin_criterios_devuelve_vacio(self):
        self.assertEqual(self.consultas.filtrar(), [])

    def test_filtrar_dni_y_estado_combina_con_o(self):
        # Semantica heredada de la version 1 (OR), documentada como deuda pendiente.
        encontradas = self.consultas.filtrar(dni="30111222", estado="RESUELTO")
        self.assertEqual({s.id for s in encontradas}, {self.s1.id, self.s2.id})

    def test_filtrar_estado_desconocido_no_falla(self):
        self.assertEqual(self.consultas.filtrar(estado="ARCHIVADO"), [])

    def test_reporte_estadistico(self):
        self.assertEqual(self.consultas.generar_reporte(),
                         {"total": 2, "pendientes": 1, "resueltos": 1})

    def test_reporte_sin_datos(self):
        vacio = ConsultaService(RepositorioEnMemoria())
        self.assertEqual(vacio.generar_reporte(),
                         {"total": 0, "pendientes": 0, "resueltos": 0})


if __name__ == "__main__":
    unittest.main()

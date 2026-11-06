"""Pruebas de contrato: toda implementacion de SolicitudRepository debe cumplirlas (LSP)."""
import os
import tempfile
import unittest

from solicitudes import (Estudiante, RepositorioEnMemoria, RepositorioError,
                         RepositorioJSON, Solicitud)
from solicitudes.modelos import EstadoSolicitud


def solicitud(id_sol=1, estado=EstadoSolicitud.PENDIENTE):
    return Solicitud(id_sol, Estudiante("30111222", "Estudiante Demo"),
                     "Reclamo", "Desc", "2026-11-05", estado=estado)


class ContratoRepositorio:
    """Mixin con las pruebas comunes; las subclases definen crear_repositorio()."""

    def crear_repositorio(self):
        raise NotImplementedError

    def test_repositorio_nuevo_esta_vacio(self):
        self.assertEqual(self.crear_repositorio().obtener_todas(), [])

    def test_guardar_y_obtener(self):
        repo = self.crear_repositorio()
        repo.guardar_todas([solicitud(1), solicitud(2, EstadoSolicitud.RESUELTO)])
        obtenidas = repo.obtener_todas()
        self.assertEqual([s.id for s in obtenidas], [1, 2])
        self.assertEqual(obtenidas[1].estado, EstadoSolicitud.RESUELTO)

    def test_guardar_reemplaza_el_contenido(self):
        repo = self.crear_repositorio()
        repo.guardar_todas([solicitud(1), solicitud(2)])
        repo.guardar_todas([solicitud(3)])
        self.assertEqual([s.id for s in repo.obtener_todas()], [3])

    def test_modificar_lo_leido_no_persiste_sin_guardar(self):
        repo = self.crear_repositorio()
        repo.guardar_todas([solicitud(1)])
        repo.obtener_todas()[0].asignar_a("Cambio sin guardar")
        self.assertEqual(repo.obtener_todas()[0].responsable.nombre, "SIN ASIGNAR")


class TestRepositorioEnMemoria(ContratoRepositorio, unittest.TestCase):
    def crear_repositorio(self):
        return RepositorioEnMemoria()


class TestRepositorioJSON(ContratoRepositorio, unittest.TestCase):
    def setUp(self):
        self._carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self._carpeta.cleanup)
        self.archivo = os.path.join(self._carpeta.name, "solicitudes.json")

    def crear_repositorio(self):
        return RepositorioJSON(self.archivo)

    def test_se_crea_el_archivo_si_no_existe(self):
        self.crear_repositorio()
        self.assertTrue(os.path.exists(self.archivo))

    def test_persiste_entre_instancias(self):
        self.crear_repositorio().guardar_todas([solicitud(1)])
        self.assertEqual(len(self.crear_repositorio().obtener_todas()), 1)

    def test_json_corrupto_lanza_repositorio_error_y_no_toca_el_archivo(self):
        self.crear_repositorio()
        with open(self.archivo, "w", encoding="utf-8") as f:
            f.write("{esto no es json")
        repo = RepositorioJSON(self.archivo)
        with self.assertRaises(RepositorioError):
            repo.obtener_todas()
        with open(self.archivo, encoding="utf-8") as f:
            self.assertEqual(f.read(), "{esto no es json")

    def test_registro_con_clave_faltante_lanza_repositorio_error(self):
        self.crear_repositorio()
        with open(self.archivo, "w", encoding="utf-8") as f:
            f.write('[{"id": 1}]')
        with self.assertRaises(RepositorioError):
            RepositorioJSON(self.archivo).obtener_todas()

    def test_estado_desconocido_en_archivo_lanza_repositorio_error(self):
        self.crear_repositorio().guardar_todas([solicitud(1)])
        with open(self.archivo, encoding="utf-8") as f:
            contenido = f.read().replace("PENDIENTE", "ARCHIVADO")
        with open(self.archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        with self.assertRaises(RepositorioError):
            RepositorioJSON(self.archivo).obtener_todas()

    def test_error_de_escritura_lanza_repositorio_error(self):
        ruta_imposible = os.path.join(self._carpeta.name, "no_existe", "solicitudes.json")
        with self.assertRaises(RepositorioError):
            RepositorioJSON(ruta_imposible)

    def test_no_queda_archivo_temporal(self):
        self.crear_repositorio().guardar_todas([solicitud(1)])
        self.assertFalse(os.path.exists(self.archivo + ".tmp"))


if __name__ == "__main__":
    unittest.main()

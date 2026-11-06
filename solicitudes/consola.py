"""Capa de presentacion: fachada de consola compatible con la API de la version 1.

Conserva la firma y los mensajes originales de ejecutar_operacion para demostrar
que el comportamiento externo se mantiene. El codigo nuevo debe usar los
servicios directamente, sin pasar por esta clase.
"""
from dataclasses import dataclass
from typing import Optional

from .excepciones import (DatosInvalidosError, EstadoInvalidoError,
                          RepositorioError, SolicitudNoEncontradaError)
from .modelos import DatosNuevaSolicitud
from .repositorio import RepositorioJSON, solicitud_a_dict
from .servicios import ConsultaService, SolicitudService


@dataclass(frozen=True)
class Peticion:
    """Parameter Object que reemplaza los 8 parametros sueltos de la version 1."""
    id_sol: Optional[int] = None
    dni: Optional[str] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    desc: Optional[str] = None
    estado: Optional[str] = None
    resp: Optional[str] = None


class GestorSolicitudesConsola:
    def __init__(self, archivo="solicitudes.json"):
        repositorio = RepositorioJSON(archivo)
        self._comandos = SolicitudService(repositorio)
        self._consultas = ConsultaService(repositorio)
        self._operaciones = {
            "CREAR": self._crear,
            "CAMBIAR_ESTADO": self._cambiar_estado,
            "ASIGNAR": self._asignar,
            "FILTRAR": self._filtrar,
            "REPORTE": self._reporte,
        }

    def ejecutar_operacion(self, op, id_sol=None, dni=None, nombre=None,
                           tipo=None, desc=None, estado=None, resp=None):
        peticion = Peticion(id_sol, dni, nombre, tipo, desc, estado, resp)
        operacion = self._operaciones.get(op)
        if operacion is None:
            return None
        try:
            return operacion(peticion)
        except RepositorioError:
            print("Error: no se pudo acceder al archivo de datos.")
            return None

    def _crear(self, p):
        try:
            self._comandos.crear_solicitud(
                DatosNuevaSolicitud(p.dni, p.nombre, p.tipo, p.desc))
        except DatosInvalidosError:
            print("Error: Datos invalidos.")
            return False
        print("Solicitud creada con exito.")
        return True

    def _cambiar_estado(self, p):
        try:
            self._comandos.cambiar_estado(p.id_sol, p.estado)
        except SolicitudNoEncontradaError:
            print("Solicitud no encontrada.")
            return False
        except EstadoInvalidoError:
            print("Estado invalido.")
            return False
        print(f"Estado de la solicitud {p.id_sol} actualizado a {p.estado}.")
        return True

    def _asignar(self, p):
        try:
            self._comandos.asignar_responsable(p.id_sol, p.resp)
        except SolicitudNoEncontradaError:
            print("Solicitud no encontrada.")
            return False
        print(f"Responsable {p.resp} asignado a la solicitud {p.id_sol}.")
        return True

    def _filtrar(self, p):
        encontradas = [solicitud_a_dict(s)
                       for s in self._consultas.filtrar(dni=p.dni, estado=p.estado)]
        print(f"--- RESULTADOS DE BUSQUEDA ({len(encontradas)}) ---")
        for r in encontradas:
            print(f"ID: {r['id']} | DNI: {r['dni']} | Estudiante: {r['estudiante']} "
                  f"| Tipo: {r['tipo']} | Estado: {r['estado']} | Resp: {r['responsable']}")
        return encontradas

    def _reporte(self, _peticion):
        reporte = self._consultas.generar_reporte()
        print("=== REPORTE GENERAL DE SOLICITUDES ===")
        print(f"Total: {reporte['total']} | Pendientes: {reporte['pendientes']} "
              f"| Resueltos: {reporte['resueltos']}")
        return reporte

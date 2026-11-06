"""Capa de servicio: casos de uso. Depende de abstracciones, no de archivos (DIP)."""
from datetime import date
from typing import Callable, List, Optional

from .excepciones import SolicitudNoEncontradaError
from .modelos import DatosNuevaSolicitud, EstadoSolicitud, Estudiante, Solicitud
from .repositorio import SolicitudLectura, SolicitudRepository


class SolicitudService:
    """Casos de uso que modifican datos: necesita leer y escribir."""

    def __init__(self, repositorio: SolicitudRepository,
                 hoy: Callable[[], date] = date.today):
        self._repo = repositorio
        self._hoy = hoy

    def crear_solicitud(self, datos: DatosNuevaSolicitud) -> Solicitud:
        datos.validar()
        solicitudes = self._repo.obtener_todas()
        nueva = Solicitud(
            id=self._siguiente_id(solicitudes),
            estudiante=Estudiante(datos.dni, datos.estudiante),
            tipo=datos.tipo,
            descripcion=datos.descripcion,
            fecha=str(self._hoy()),
        )
        solicitudes.append(nueva)
        self._repo.guardar_todas(solicitudes)
        return nueva

    def cambiar_estado(self, id_sol: int, nuevo_estado) -> Solicitud:
        solicitudes = self._repo.obtener_todas()
        solicitud = self._buscar(solicitudes, id_sol)
        solicitud.cambiar_estado(nuevo_estado)
        self._repo.guardar_todas(solicitudes)
        return solicitud

    def asignar_responsable(self, id_sol: int, nombre_responsable) -> Solicitud:
        solicitudes = self._repo.obtener_todas()
        solicitud = self._buscar(solicitudes, id_sol)
        solicitud.asignar_a(nombre_responsable)
        self._repo.guardar_todas(solicitudes)
        return solicitud

    @staticmethod
    def _siguiente_id(solicitudes: List[Solicitud]) -> int:
        return max((s.id for s in solicitudes), default=0) + 1

    @staticmethod
    def _buscar(solicitudes: List[Solicitud], id_sol: int) -> Solicitud:
        for solicitud in solicitudes:
            if solicitud.id == id_sol:
                return solicitud
        raise SolicitudNoEncontradaError(id_sol)


class ConsultaService:
    """Casos de uso de solo lectura: depende unicamente del contrato de lectura (ISP)."""

    def __init__(self, lector: SolicitudLectura):
        self._lector = lector

    def filtrar(self, dni: Optional[str] = None, estado=None) -> List[Solicitud]:
        """Mantiene la semantica de la version 1: coincide por DNI o por estado."""
        estado_texto = estado.value if isinstance(estado, EstadoSolicitud) else estado
        return [
            s for s in self._lector.obtener_todas()
            if (dni and s.estudiante.dni == dni)
            or (estado_texto and s.estado.value == estado_texto)
        ]

    def generar_reporte(self) -> dict:
        solicitudes = self._lector.obtener_todas()
        return {
            "total": len(solicitudes),
            "pendientes": self._contar(solicitudes, EstadoSolicitud.PENDIENTE),
            "resueltos": self._contar(solicitudes, EstadoSolicitud.RESUELTO),
        }

    @staticmethod
    def _contar(solicitudes: List[Solicitud], estado: EstadoSolicitud) -> int:
        return sum(1 for s in solicitudes if s.estado == estado)

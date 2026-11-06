"""Capa de dominio: entidades y reglas de negocio, sin entrada/salida."""
from dataclasses import dataclass
from enum import Enum

from .excepciones import DatosInvalidosError, EstadoInvalidoError

LARGO_MINIMO_DNI = 7
TEXTO_SIN_ASIGNAR = "SIN ASIGNAR"


class EstadoSolicitud(Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    RECHAZADO = "RECHAZADO"

    @classmethod
    def desde_texto(cls, valor):
        """Convierte un texto (o un estado ya tipado) en EstadoSolicitud."""
        if isinstance(valor, cls):
            return valor
        for estado in cls:
            if estado.value == valor:
                return estado
        raise EstadoInvalidoError(valor)


@dataclass(frozen=True)
class Estudiante:
    dni: str
    nombre: str


@dataclass(frozen=True)
class Responsable:
    nombre: str


SIN_ASIGNAR = Responsable(TEXTO_SIN_ASIGNAR)


@dataclass(frozen=True)
class DatosNuevaSolicitud:
    """Parameter Object: agrupa los datos de entrada para crear una solicitud."""
    dni: str
    estudiante: str
    tipo: str
    descripcion: str

    def validar(self):
        """Regla de negocio original: DNI de al menos 7 caracteres y tipo presente."""
        if not self.dni or not self.tipo or len(self.dni) < LARGO_MINIMO_DNI:
            raise DatosInvalidosError("DNI o tipo de solicitud invalidos")


@dataclass
class Solicitud:
    id: int
    estudiante: Estudiante
    tipo: str
    descripcion: str
    fecha: str
    estado: EstadoSolicitud = EstadoSolicitud.PENDIENTE
    responsable: Responsable = SIN_ASIGNAR

    def cambiar_estado(self, nuevo_estado):
        self.estado = EstadoSolicitud.desde_texto(nuevo_estado)

    def asignar_a(self, nombre_responsable):
        self.responsable = Responsable(nombre_responsable)

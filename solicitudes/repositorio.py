"""Capa de persistencia: contratos (ISP) e implementaciones intercambiables (LSP)."""
import copy
import json
import os
from abc import ABC, abstractmethod
from typing import List

from .excepciones import RepositorioError
from .modelos import EstadoSolicitud, Estudiante, Responsable, Solicitud


class SolicitudLectura(ABC):
    """Contrato minimo para quien solo consulta solicitudes."""

    @abstractmethod
    def obtener_todas(self) -> List[Solicitud]:
        """Devuelve copias de las solicitudes almacenadas."""


class SolicitudEscritura(ABC):
    """Contrato minimo para quien solo persiste solicitudes."""

    @abstractmethod
    def guardar_todas(self, solicitudes: List[Solicitud]) -> None:
        """Reemplaza el contenido almacenado por las solicitudes recibidas."""


class SolicitudRepository(SolicitudLectura, SolicitudEscritura):
    """Contrato completo, para quien necesita leer y escribir."""


def solicitud_a_dict(solicitud: Solicitud) -> dict:
    """Formato de almacenamiento: mismas claves y orden que la version 1."""
    return {
        "id": solicitud.id,
        "dni": solicitud.estudiante.dni,
        "estudiante": solicitud.estudiante.nombre,
        "tipo": solicitud.tipo,
        "descripcion": solicitud.descripcion,
        "estado": solicitud.estado.value,
        "responsable": solicitud.responsable.nombre,
        "fecha": solicitud.fecha,
    }


def solicitud_desde_dict(item: dict) -> Solicitud:
    return Solicitud(
        id=item["id"],
        estudiante=Estudiante(item["dni"], item["estudiante"]),
        tipo=item["tipo"],
        descripcion=item["descripcion"],
        estado=EstadoSolicitud(item["estado"]),
        responsable=Responsable(item["responsable"]),
        fecha=item["fecha"],
    )


class RepositorioJSON(SolicitudRepository):
    def __init__(self, archivo="solicitudes.json"):
        self.archivo = archivo
        if not os.path.exists(self.archivo):
            self._escribir([])

    def obtener_todas(self) -> List[Solicitud]:
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            return [solicitud_desde_dict(item) for item in datos]
        except (OSError, ValueError, KeyError, TypeError) as error:
            # No se devuelve una lista vacia: un guardado posterior
            # sobrescribiria el archivo y se perderian los datos existentes.
            raise RepositorioError(f"No se pudo leer {self.archivo}: {error}") from error

    def guardar_todas(self, solicitudes: List[Solicitud]) -> None:
        self._escribir([solicitud_a_dict(s) for s in solicitudes])

    def _escribir(self, datos):
        temporal = self.archivo + ".tmp"
        try:
            with open(temporal, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4)
            os.replace(temporal, self.archivo)  # escritura atomica
        except OSError as error:
            raise RepositorioError(f"No se pudo escribir {self.archivo}: {error}") from error


class RepositorioEnMemoria(SolicitudRepository):
    """Segunda implementacion del contrato: util para pruebas y como prueba de LSP."""

    def __init__(self):
        self._almacen: List[Solicitud] = []

    def obtener_todas(self) -> List[Solicitud]:
        return copy.deepcopy(self._almacen)

    def guardar_todas(self, solicitudes: List[Solicitud]) -> None:
        self._almacen = copy.deepcopy(solicitudes)

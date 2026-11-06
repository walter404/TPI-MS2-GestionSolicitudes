"""Excepciones propias del dominio de solicitudes academicas."""


class SolicitudesError(Exception):
    """Base de todas las excepciones del sistema."""


class DatosInvalidosError(SolicitudesError):
    """Los datos para crear una solicitud no cumplen las reglas de negocio."""


class EstadoInvalidoError(SolicitudesError):
    """El texto recibido no corresponde a ningun EstadoSolicitud."""

    def __init__(self, valor):
        super().__init__(f"Estado invalido: {valor!r}")
        self.valor = valor


class SolicitudNoEncontradaError(SolicitudesError):
    """No existe una solicitud con el identificador pedido."""

    def __init__(self, id_sol):
        super().__init__(f"Solicitud no encontrada: {id_sol!r}")
        self.id_sol = id_sol


class RepositorioError(SolicitudesError):
    """No se pudo leer o escribir el almacenamiento de solicitudes."""

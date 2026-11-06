"""Demostracion: python -m solicitudes (usa datos sinteticos)."""
import os
import tempfile

from . import GestorSolicitudesConsola


def main():
    with tempfile.TemporaryDirectory() as carpeta:
        gestor = GestorSolicitudesConsola(os.path.join(carpeta, "demo.json"))
        gestor.ejecutar_operacion("CREAR", dni="30111222", nombre="Estudiante Demo 1",
                                  tipo="Equivalencia", desc="Pedido de equivalencia")
        gestor.ejecutar_operacion("CREAR", dni="123", nombre="Estudiante Demo 2",
                                  tipo="Reclamo", desc="DNI demasiado corto")
        gestor.ejecutar_operacion("ASIGNAR", id_sol=1, resp="Area Alumnos")
        gestor.ejecutar_operacion("CAMBIAR_ESTADO", id_sol=1, estado="RESUELTO")
        gestor.ejecutar_operacion("FILTRAR", estado="RESUELTO")
        gestor.ejecutar_operacion("REPORTE")


if __name__ == "__main__":
    main()

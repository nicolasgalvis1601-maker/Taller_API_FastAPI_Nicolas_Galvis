"""Esquemas Pydantic: validacion de entrada y forma de las respuestas."""

from .autor import AutorActualizar, AutorCrear, AutorLeer, AutorResumen
from .categoria import CategoriaActualizar, CategoriaCrear, CategoriaLeer, CategoriaResumen
from .libro import LibroActualizar, LibroCrear, LibroLeer, LibroResumen, OrdenLibros
from .prestamo import EstadoPrestamo, PrestamoCrear, PrestamoDevolucion, PrestamoLeer
from .reporte import (
    LibroMasPrestado,
    LibrosPorCategoria,
    PrestamoVencido,
    ResumenAutor,
    ResumenGeneral,
    SocioConMultas,
)
from .socio import SocioActualizar, SocioCrear, SocioLeer, SocioResumen

__all__ = [
    "AutorActualizar", "AutorCrear", "AutorLeer", "AutorResumen",
    "CategoriaActualizar", "CategoriaCrear", "CategoriaLeer", "CategoriaResumen",
    "LibroActualizar", "LibroCrear", "LibroLeer", "LibroResumen", "OrdenLibros",
    "EstadoPrestamo", "PrestamoCrear", "PrestamoDevolucion", "PrestamoLeer",
    "LibroMasPrestado", "LibrosPorCategoria", "PrestamoVencido", "ResumenAutor",
    "ResumenGeneral", "SocioConMultas",
    "SocioActualizar", "SocioCrear", "SocioLeer", "SocioResumen",
]

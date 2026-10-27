"""Modelos SQLAlchemy. Importarlos aqui los registra en Base.metadata."""

from .autor import Autor
from .categoria import Categoria
from .libro import Libro
from .libro_categoria import libro_categoria
from .prestamo import Prestamo
from .socio import Socio

__all__ = ["Autor", "Categoria", "Libro", "Prestamo", "Socio", "libro_categoria"]

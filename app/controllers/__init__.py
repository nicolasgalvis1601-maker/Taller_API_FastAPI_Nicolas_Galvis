"""Logica de negocio, independiente de HTTP (sin HTTPException ni codigos HTTP).

Se exponen los modulos (no las funciones sueltas) porque tienen funciones con el
mismo nombre (listar, obtener, crear...). Uso:

    from app.controllers import libros
    libros.listar(db, pag)
"""

from . import autores, categorias, libros, prestamos, reportes, socios

__all__ = ["autores", "categorias", "libros", "prestamos", "reportes", "socios"]

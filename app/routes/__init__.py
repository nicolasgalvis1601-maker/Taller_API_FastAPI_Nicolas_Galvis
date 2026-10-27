"""Enrutadores HTTP de la aplicacion."""

from fastapi import APIRouter

from . import autores, categorias, libros, prestamos, reportes, socios

api_router = APIRouter()
api_router.include_router(autores.router)
api_router.include_router(categorias.router)
api_router.include_router(libros.router)
api_router.include_router(socios.router)
api_router.include_router(prestamos.router)
api_router.include_router(reportes.router)

__all__ = ["api_router"]

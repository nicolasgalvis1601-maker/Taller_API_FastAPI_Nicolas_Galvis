"""Esquemas de respuesta de los reportes (una fila de cada consulta SQL)."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class _Fila(BaseModel):
    # Las filas llegan como diccionarios (RowMapping) o como objetos Row.
    model_config = ConfigDict(from_attributes=True)


class LibroMasPrestado(_Fila):
    libro_id: int
    titulo: str
    autor: str
    total_prestamos: int


class LibrosPorCategoria(_Fila):
    categoria_id: int
    categoria: str
    total_libros: int


class PrestamoVencido(_Fila):
    prestamo_id: int
    titulo: str
    socio: str
    email: str
    fecha_limite: date
    dias_retraso: int


class SocioConMultas(_Fila):
    socio_id: int
    nombre: str
    email: str
    total_multas: float
    prestamos_con_multa: int


class ResumenAutor(_Fila):
    autor_id: int
    autor: str
    total_libros: int
    total_ejemplares: int
    total_prestamos: int


class ResumenGeneral(_Fila):
    total_libros: int
    total_ejemplares: int
    prestados: int  # prestamos sin devolver
    socios_activos: int
    prestamos_vencidos: int
    total_multas: float

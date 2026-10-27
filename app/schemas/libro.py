from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.limites import MAX_INT
from ._comun import formato_titulo, no_mayor_que_anio_actual
from .autor import AutorResumen
from .categoria import CategoriaResumen

# [0-9] y no \d: en Pydantic \d tambien acepta digitos de otros alfabetos (p. ej. "٣").
PATRON_ISBN = r"^[0-9]{13}$"


class OrdenLibros(str, Enum):
    """Valores permitidos en ?orden= de GET /libros."""

    titulo = "titulo"
    anio = "anio"
    anio_desc = "-anio"


def sin_repetidos(valor: list[int] | None) -> list[int] | None:
    if valor is not None and len(set(valor)) != len(valor):
        raise ValueError("categoria_ids no puede tener ids repetidos")
    return valor


# Cada id de la lista debe ser un entero positivo que quepa en INTEGER.
IdCategoria = Annotated[int, Field(gt=0, le=MAX_INT)]


class LibroCrear(BaseModel):
    titulo: str = Field(min_length=1, max_length=150, examples=["Cien años de soledad"])
    isbn: str = Field(pattern=PATRON_ISBN, examples=["9780307474728"])
    anio_publicacion: int = Field(ge=1450, examples=[1967])
    ejemplares: int = Field(ge=1, le=50, examples=[2])
    autor_id: int = Field(gt=0, le=MAX_INT, examples=[1])
    categoria_ids: list[IdCategoria] = Field(min_length=1, max_length=5, examples=[[1, 2]])

    validar_titulo = field_validator("titulo", mode="before")(formato_titulo)
    validar_anio = field_validator("anio_publicacion")(no_mayor_que_anio_actual)
    validar_categorias = field_validator("categoria_ids")(sin_repetidos)


class LibroActualizar(BaseModel):
    """PATCH: si se envia categoria_ids, reemplaza todas las categorias del libro."""

    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    isbn: str | None = Field(default=None, pattern=PATRON_ISBN)
    anio_publicacion: int | None = Field(default=None, ge=1450)
    # Ademas de 1..50, el controlador comprueba que no quede por debajo de los
    # prestamos sin devolver (422).
    ejemplares: int | None = Field(default=None, ge=1, le=50)
    autor_id: int | None = Field(default=None, gt=0, le=MAX_INT)
    categoria_ids: list[IdCategoria] | None = Field(default=None, min_length=1, max_length=5)

    validar_titulo = field_validator("titulo", mode="before")(formato_titulo)
    validar_anio = field_validator("anio_publicacion")(no_mayor_que_anio_actual)
    validar_categorias = field_validator("categoria_ids")(sin_repetidos)


class LibroLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str
    anio_publicacion: int
    ejemplares: int
    disponibles: int  # calculado: ejemplares - prestamos sin devolver
    autor: AutorResumen
    categorias: list[CategoriaResumen]


class LibroResumen(BaseModel):
    """Version corta para anidar dentro de un prestamo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str

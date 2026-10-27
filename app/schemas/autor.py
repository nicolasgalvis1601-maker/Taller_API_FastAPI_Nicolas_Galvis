from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._comun import formato_titulo, limpiar_espacios, no_mayor_que_anio_actual


class AutorCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Gabriel García Márquez"])
    nacionalidad: str | None = Field(default=None, min_length=1, max_length=60, examples=["Colombiana"])
    anio_nacimiento: int | None = Field(default=None, ge=1000, examples=[1927])

    validar_nombre = field_validator("nombre", mode="before")(formato_titulo)
    validar_nacionalidad = field_validator("nacionalidad", mode="before")(limpiar_espacios)
    validar_anio = field_validator("anio_nacimiento")(no_mayor_que_anio_actual)


class AutorActualizar(BaseModel):
    """PATCH: todos los campos son opcionales; solo se cambian los enviados."""

    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, min_length=1, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    validar_nombre = field_validator("nombre", mode="before")(formato_titulo)
    validar_nacionalidad = field_validator("nacionalidad", mode="before")(limpiar_espacios)
    validar_anio = field_validator("anio_nacimiento")(no_mayor_que_anio_actual)


class AutorLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nacionalidad: str | None
    anio_nacimiento: int | None


class AutorResumen(BaseModel):
    """Version corta para anidar dentro de un libro."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str

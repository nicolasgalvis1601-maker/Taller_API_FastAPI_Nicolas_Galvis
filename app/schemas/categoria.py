from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._comun import limpiar_espacios, minusculas


class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=3, max_length=50, examples=["Realismo Mágico"])
    descripcion: str | None = Field(default=None, max_length=200, examples=["Lo fantástico en lo cotidiano"])

    # Se guarda en minusculas: "Realismo Mágico" -> "realismo mágico".
    validar_nombre = field_validator("nombre", mode="before")(minusculas)
    validar_descripcion = field_validator("descripcion", mode="before")(limpiar_espacios)


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    validar_nombre = field_validator("nombre", mode="before")(minusculas)
    validar_descripcion = field_validator("descripcion", mode="before")(limpiar_espacios)


class CategoriaLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None


class CategoriaResumen(BaseModel):
    """Version corta para anidar dentro de un libro."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str

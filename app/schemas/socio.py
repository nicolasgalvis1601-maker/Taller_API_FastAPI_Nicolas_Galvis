from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ._comun import formato_titulo, limpiar_espacios

# De 7 a 15 caracteres: solo digitos, espacios o "+".
PATRON_TELEFONO = r"^[0-9 +]{7,15}$"


def email_minusculas(valor: str | None) -> str | None:
    """Se guarda en minusculas: "ANA@example.com" -> "ana@example.com"."""
    if valor is None:
        return valor
    valor = valor.lower()
    if len(valor) > 150:
        raise ValueError("El email admite como máximo 150 caracteres")
    return valor


class SocioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Ana Torres"])
    email: EmailStr = Field(examples=["ana@example.com"])
    telefono: str | None = Field(default=None, pattern=PATRON_TELEFONO, examples=["+57 300 1234567"])

    validar_nombre = field_validator("nombre", mode="before")(formato_titulo)
    validar_email = field_validator("email")(email_minusculas)
    validar_telefono = field_validator("telefono", mode="before")(limpiar_espacios)


class SocioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, pattern=PATRON_TELEFONO)
    activo: bool | None = None  # permite reactivar un socio desactivado

    validar_nombre = field_validator("nombre", mode="before")(formato_titulo)
    validar_email = field_validator("email")(email_minusculas)
    validar_telefono = field_validator("telefono", mode="before")(limpiar_espacios)


class SocioLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    telefono: str | None
    activo: bool
    fecha_alta: datetime


class SocioResumen(BaseModel):
    """Version corta para anidar dentro de un prestamo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str

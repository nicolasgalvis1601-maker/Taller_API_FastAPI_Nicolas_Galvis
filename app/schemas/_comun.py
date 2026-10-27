"""Funciones de limpieza y validacion compartidas por varios esquemas."""

from datetime import date
from typing import Any


def limpiar_espacios(valor: Any) -> Any:
    """Quita los espacios sobrantes: "  la   casa " -> "la casa".

    Se usa con mode="before" para que min_length/max_length se comprueben sobre
    el texto YA limpio.
    """
    if not isinstance(valor, str):
        return valor  # None o un tipo incorrecto: Pydantic se encarga.
    return " ".join(valor.split())


def formato_titulo(valor: Any) -> Any:
    """Limpia espacios y pone cada palabra con la primera letra en mayuscula.

    "cien años de soledad" -> "Cien Años De Soledad"
    No usa str.title() porque convierte "o'brien" en "O'Brien" pero "don't" en "Don'T".
    """
    valor = limpiar_espacios(valor)
    if not isinstance(valor, str):
        return valor
    return " ".join(palabra[:1].upper() + palabra[1:].lower() for palabra in valor.split(" "))


def minusculas(valor: Any) -> Any:
    """Limpia espacios y pasa todo a minusculas: " Realismo  Mágico" -> "realismo mágico"."""
    valor = limpiar_espacios(valor)
    return valor.lower() if isinstance(valor, str) else valor


def no_mayor_que_anio_actual(valor: int | None) -> int | None:
    """El "año actual" se calcula en cada peticion (no al arrancar la API)."""
    if valor is not None and valor > date.today().year:
        raise ValueError(f"El año no puede ser mayor que {date.today().year}")
    return valor


def no_futura(valor: date | None) -> date | None:
    if valor is not None and valor > date.today():
        raise ValueError("La fecha no puede ser futura")
    return valor

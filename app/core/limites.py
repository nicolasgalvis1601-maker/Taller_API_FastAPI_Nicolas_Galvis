"""Limites que reflejan las columnas de la base de datos.

Sin estos limites, un numero demasiado grande (por ejemplo /libros/99999999999)
llega hasta PostgreSQL, no cabe en una columna INTEGER y la API responde 500.
Con ellos, FastAPI lo rechaza antes con un 422.
"""

from typing import Annotated

from fastapi import Path

# Las columnas INTEGER de PostgreSQL son de 32 bits con signo.
MAX_INT = 2_147_483_647

# Tipo reutilizable para los ids que llegan en la URL.
IdPath = Annotated[int, Path(gt=0, le=MAX_INT)]

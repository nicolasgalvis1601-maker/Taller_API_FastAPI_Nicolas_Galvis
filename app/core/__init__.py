"""Configuracion e infraestructura compartida.

`database` y `dependencies` NO se reexportan aqui a proposito: importarlos exige
tener DATABASE_URL configurada. Importalos directamente:
`from app.core.database import Base` / `from app.core.dependencies import SessionDep`.
"""

from .exceptions import Conflicto, ErrorAplicacion, NoEncontrado, ReglaNegocio
from .limites import MAX_INT, IdPath

__all__ = ["Conflicto", "ErrorAplicacion", "IdPath", "MAX_INT", "NoEncontrado", "ReglaNegocio"]

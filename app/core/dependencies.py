from collections.abc import Generator
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from .database import SessionLocal
from .limites import MAX_INT


def get_db() -> Generator[Session, None, None]:
    """Abre una sesion por peticion y la cierra al terminar."""
    with SessionLocal() as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]


@dataclass(frozen=True)
class Paginacion:
    skip: int
    limit: int


def paginacion(
    skip: int = Query(0, ge=0, le=MAX_INT, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros (1 a 100)"),
) -> Paginacion:
    """Dependencia reutilizable: todos los listados reciben skip y limit."""
    return Paginacion(skip=skip, limit=limit)


PaginacionDep = Annotated[Paginacion, Depends(paginacion)]

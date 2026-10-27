from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto


def confirmar(db: Session, mensaje_conflicto: str) -> None:
    """Hace commit y convierte una violacion de restriccion en un 409.

    Las validaciones previas (nombre unico, isbn unico...) cubren el caso normal,
    pero si dos peticiones llegan a la vez ambas pueden pasar la validacion y la
    segunda chocaria con la restriccion de la base de datos. Sin esto, ese choque
    se veria como un 500.
    """
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto(mensaje_conflicto) from exc


def escapar_like(texto: str) -> str:
    """Sin esto, buscar "%" o "_" funcionan como comodines y devuelven todo."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def patron_contiene(texto: str) -> str:
    """Patron para ilike: contiene el texto, sin distinguir mayusculas."""
    return f"%{escapar_like(texto.strip())}%"

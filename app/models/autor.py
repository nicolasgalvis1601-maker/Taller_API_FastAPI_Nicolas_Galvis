from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .libro import Libro


class Autor(Base):
    __tablename__ = "autores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    nacionalidad: Mapped[str | None] = mapped_column(String(60))
    anio_nacimiento: Mapped[int | None]

    # 1:N -> un autor tiene muchos libros.
    libros: Mapped[list["Libro"]] = relationship(back_populates="autor")

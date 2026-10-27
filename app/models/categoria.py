from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .libro_categoria import libro_categoria

if TYPE_CHECKING:
    from .libro import Libro


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(200))

    # N:M -> una categoria tiene muchos libros (a traves de libro_categoria).
    libros: Mapped[list["Libro"]] = relationship(
        secondary=libro_categoria, back_populates="categorias"
    )

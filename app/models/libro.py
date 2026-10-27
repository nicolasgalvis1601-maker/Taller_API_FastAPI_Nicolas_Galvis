from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .libro_categoria import libro_categoria

if TYPE_CHECKING:
    from .autor import Autor
    from .categoria import Categoria
    from .prestamo import Prestamo


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    anio_publicacion: Mapped[int]
    ejemplares: Mapped[int]
    # RESTRICT: PostgreSQL no deja borrar un autor que tenga libros.
    autor_id: Mapped[int] = mapped_column(ForeignKey("autores.id", ondelete="RESTRICT"), index=True)

    autor: Mapped["Autor"] = relationship(back_populates="libros")
    categorias: Mapped[list["Categoria"]] = relationship(
        secondary=libro_categoria, back_populates="libros", order_by="Categoria.id"
    )
    # Al borrar un libro (solo se permite si no tiene prestamos sin devolver)
    # se borra tambien su historial de prestamos ya devueltos.
    prestamos: Mapped[list["Prestamo"]] = relationship(
        back_populates="libro", cascade="all, delete-orphan", passive_deletes=True
    )

    # `prestados` (prestamos sin devolver) es un column_property que se define en
    # models/prestamo.py, porque necesita la clase Prestamo. No es una columna:
    # PostgreSQL lo calcula con una subconsulta cada vez que se lee el libro.

    @property
    def disponibles(self) -> int:
        """Campo calculado: ejemplares - prestamos sin devolver."""
        return self.ejemplares - self.prestados

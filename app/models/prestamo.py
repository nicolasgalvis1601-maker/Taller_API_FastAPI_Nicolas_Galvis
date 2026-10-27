from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from ..core.database import Base
from .libro import Libro

if TYPE_CHECKING:
    from .socio import Socio


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id", ondelete="CASCADE"), index=True)
    # RESTRICT: un socio con prestamos no se borra (se desactiva).
    socio_id: Mapped[int] = mapped_column(ForeignKey("socios.id", ondelete="RESTRICT"), index=True)
    fecha_prestamo: Mapped[date] = mapped_column(Date)
    fecha_limite: Mapped[date] = mapped_column(Date)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date)
    multa: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("0"), server_default="0")

    libro: Mapped["Libro"] = relationship(back_populates="prestamos")
    socio: Mapped["Socio"] = relationship(back_populates="prestamos")

    # El estado (activo / vencido / devuelto) NO se guarda: se calcula con las fechas
    # en el esquema PrestamoLeer y en los filtros SQL del controlador.


# Libro.prestados = numero de prestamos sin devolver de ese libro.
# Se agrega aqui porque necesita la clase Prestamo (asi se evita un import circular).
# SQL: (SELECT count(prestamos.id) FROM prestamos
#        WHERE prestamos.libro_id = libros.id AND prestamos.fecha_devolucion IS NULL)
Libro.prestados = column_property(
    select(func.count(Prestamo.id))
    .where(Prestamo.libro_id == Libro.id, Prestamo.fecha_devolucion.is_(None))
    .correlate_except(Prestamo)
    .scalar_subquery()
)

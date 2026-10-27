from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .prestamo import Prestamo


class Socio(Base):
    __tablename__ = "socios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    telefono: Mapped[str | None] = mapped_column(String(15))
    activo: Mapped[bool] = mapped_column(default=True, server_default="true")
    # La fecha la genera PostgreSQL al insertar.
    fecha_alta: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 1:N -> un socio tiene muchos prestamos.
    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="socio")

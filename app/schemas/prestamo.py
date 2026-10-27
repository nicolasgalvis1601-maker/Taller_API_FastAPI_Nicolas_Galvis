from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from ..core.limites import MAX_INT
from ._comun import no_futura
from .libro import LibroResumen
from .socio import SocioResumen


class EstadoPrestamo(str, Enum):
    activo = "activo"
    vencido = "vencido"
    devuelto = "devuelto"


class PrestamoCrear(BaseModel):
    libro_id: int = Field(gt=0, le=MAX_INT, examples=[1])
    socio_id: int = Field(gt=0, le=MAX_INT, examples=[1])
    # Por defecto hoy; se puede enviar una fecha pasada, pero no futura.
    fecha_prestamo: date = Field(default_factory=date.today, examples=["2026-10-27"])
    dias: int = Field(default=14, ge=1, le=30, examples=[14])

    validar_fecha = field_validator("fecha_prestamo")(no_futura)


class PrestamoDevolucion(BaseModel):
    """Cuerpo opcional de POST /prestamos/{id}/devolucion. Sin cuerpo = hoy."""

    fecha_devolucion: date = Field(default_factory=date.today, examples=["2026-10-27"])

    validar_fecha = field_validator("fecha_devolucion")(no_futura)


class PrestamoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None
    multa: float  # float (y no Decimal) para que el JSON muestre 6.5 y no "6.50"
    libro: LibroResumen
    socio: SocioResumen

    # El estado no se guarda en la base de datos: se calcula con las fechas.
    @computed_field
    @property
    def estado(self) -> EstadoPrestamo:
        if self.fecha_devolucion is not None:
            return EstadoPrestamo.devuelto
        if self.fecha_limite < date.today():
            return EstadoPrestamo.vencido
        return EstadoPrestamo.activo

    @computed_field
    @property
    def dias_retraso(self) -> int:
        fin = self.fecha_devolucion or date.today()
        return max(0, (fin - self.fecha_limite).days)

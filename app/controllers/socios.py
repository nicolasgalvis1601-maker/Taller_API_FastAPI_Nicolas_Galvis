from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.dependencies import Paginacion
from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Prestamo, Socio
from ..schemas import SocioActualizar, SocioCrear
from ._comun import confirmar


def listar(db: Session, pag: Paginacion, activo: bool | None = None) -> list[Socio]:
    consulta = select(Socio)
    if activo is not None:
        consulta = consulta.where(Socio.activo.is_(activo))
    consulta = consulta.order_by(Socio.nombre, Socio.id).offset(pag.skip).limit(pag.limit)
    return list(db.scalars(consulta))


def obtener(db: Session, socio_id: int) -> Socio:
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    return socio


def _validar_email_unico(db: Session, email: str, excluir_id: int | None = None) -> None:
    # El email ya llega en minusculas desde el esquema.
    consulta = select(Socio.id).where(Socio.email == email)
    if excluir_id is not None:
        consulta = consulta.where(Socio.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe un socio con el email {email}")


def crear(db: Session, datos: SocioCrear) -> Socio:
    _validar_email_unico(db, datos.email)
    socio = Socio(**datos.model_dump())
    db.add(socio)
    confirmar(db, f"Ya existe un socio con el email {datos.email}")
    db.refresh(socio)  # trae fecha_alta, que la genera PostgreSQL
    return socio


def actualizar(db: Session, socio_id: int, datos: SocioActualizar) -> Socio:
    socio = obtener(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    # nombre, email y activo son obligatorios: un null se ignora. telefono si se puede borrar.
    for campo in ("nombre", "email", "activo"):
        if campo in cambios and cambios[campo] is None:
            del cambios[campo]
    if "email" in cambios:
        _validar_email_unico(db, cambios["email"], excluir_id=socio_id)
    for campo, valor in cambios.items():
        setattr(socio, campo, valor)
    confirmar(db, f"Ya existe un socio con el email {cambios.get('email')}")
    return socio


def eliminar(db: Session, socio_id: int) -> None:
    """Borrado fisico si no tiene prestamos; borrado logico si solo tiene devueltos."""
    socio = obtener(db, socio_id)
    total, sin_devolver = db.execute(
        select(
            func.count(Prestamo.id),
            func.count(Prestamo.id).filter(Prestamo.fecha_devolucion.is_(None)),
        ).where(Prestamo.socio_id == socio_id)
    ).one()

    if sin_devolver:
        raise Conflicto(f"El socio tiene {sin_devolver} préstamo(s) sin devolver; no se puede eliminar")
    if total:
        socio.activo = False  # tiene historial: se conserva y se desactiva
    else:
        db.delete(socio)
    confirmar(db, "El socio tiene préstamos; no se puede eliminar")

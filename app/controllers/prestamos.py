from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.dependencies import Paginacion
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models import Libro, Prestamo, Socio
from ..schemas import EstadoPrestamo, PrestamoCrear, PrestamoDevolucion
from . import socios as socios_ctrl

MAX_PRESTAMOS = 3
MULTA_POR_DIA = Decimal("0.50")


def condicion_estado(estado: EstadoPrestamo, hoy: date | None = None):
    """Traduce un estado a condiciones SQL (el estado no es una columna)."""
    hoy = hoy or date.today()
    if estado == EstadoPrestamo.devuelto:
        return (Prestamo.fecha_devolucion.is_not(None),)
    if estado == EstadoPrestamo.vencido:
        return (Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite < hoy)
    return (Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite >= hoy)  # activo


def _consulta_base():
    return select(Prestamo).options(selectinload(Prestamo.libro), selectinload(Prestamo.socio))


def listar(
    db: Session,
    pag: Paginacion,
    estado: EstadoPrestamo | None = None,
    socio_id: int | None = None,
    libro_id: int | None = None,
) -> list[Prestamo]:
    consulta = _consulta_base()
    if estado is not None:
        consulta = consulta.where(*condicion_estado(estado))
    if socio_id is not None:
        consulta = consulta.where(Prestamo.socio_id == socio_id)
    if libro_id is not None:
        consulta = consulta.where(Prestamo.libro_id == libro_id)
    consulta = (
        consulta.order_by(Prestamo.fecha_prestamo.desc(), Prestamo.id.desc())
        .offset(pag.skip)
        .limit(pag.limit)
    )
    return list(db.scalars(consulta))


def listar_de_socio(
    db: Session, socio_id: int, pag: Paginacion, estado: EstadoPrestamo | None = None
) -> list[Prestamo]:
    socios_ctrl.obtener(db, socio_id)  # 404 si el socio no existe
    return listar(db, pag, estado=estado, socio_id=socio_id)


def obtener(db: Session, prestamo_id: int) -> Prestamo:
    prestamo = db.scalar(_consulta_base().where(Prestamo.id == prestamo_id))
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    return prestamo


def _recargar(db: Session, prestamo: Prestamo) -> Prestamo:
    prestamo_id = prestamo.id
    db.expire(prestamo)
    return obtener(db, prestamo_id)


def crear(db: Session, datos: PrestamoCrear) -> Prestamo:
    """Registra un prestamo comprobando las reglas R1 a R8 en orden."""
    hoy = date.today()

    # with_for_update bloquea las filas del socio y del libro hasta el commit: si
    # llegan dos prestamos a la vez, el segundo espera y vuelve a contar, asi no
    # se presta un ejemplar que ya no existe ni se pasa del maximo de 3.
    # R1: el socio existe
    socio = db.get(Socio, datos.socio_id, with_for_update=True)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")

    # R2: el libro existe
    libro = db.get(Libro, datos.libro_id, with_for_update=True)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")

    # R3: el socio esta activo
    if not socio.activo:
        raise ReglaNegocio("El socio no está activo")

    # Una sola consulta cuenta los prestamos sin devolver del socio, los vencidos
    # y los que son de este mismo libro.
    sin_devolver = Prestamo.fecha_devolucion.is_(None)
    pendientes, vencidos, mismo_libro = db.execute(
        select(
            func.count(Prestamo.id),
            func.count(Prestamo.id).filter(Prestamo.fecha_limite < hoy),
            func.count(Prestamo.id).filter(Prestamo.libro_id == libro.id),
        ).where(Prestamo.socio_id == socio.id, sin_devolver)
    ).one()

    # R4: el socio no tiene prestamos vencidos
    if vencidos:
        raise ReglaNegocio("El socio tiene préstamos vencidos")

    # R5: menos de 3 prestamos sin devolver
    if pendientes >= MAX_PRESTAMOS:
        raise ReglaNegocio(f"Máximo de {MAX_PRESTAMOS} préstamos")

    # R6: no tiene ya ese mismo libro sin devolver
    if mismo_libro:
        raise Conflicto("El socio ya tiene este libro prestado sin devolver")

    # R7: hay ejemplares disponibles
    prestados = db.scalar(
        select(func.count(Prestamo.id)).where(Prestamo.libro_id == libro.id, sin_devolver)
    )
    if prestados >= libro.ejemplares:
        raise ReglaNegocio("No hay ejemplares disponibles")

    # R8: fecha_limite = fecha_prestamo + dias
    prestamo = Prestamo(
        libro_id=libro.id,
        socio_id=socio.id,
        fecha_prestamo=datos.fecha_prestamo,
        fecha_limite=datos.fecha_prestamo + timedelta(days=datos.dias),
        multa=Decimal("0"),
    )
    db.add(prestamo)
    db.commit()
    return _recargar(db, prestamo)


def devolver(db: Session, prestamo_id: int, datos: PrestamoDevolucion) -> Prestamo:
    """Registra la devolucion aplicando las reglas R9 y R10."""
    # R9: el prestamo existe (404)... (bloqueado para que no se devuelva dos veces a la vez)
    prestamo = db.get(Prestamo, prestamo_id, with_for_update=True)
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    # ...no fue devuelto antes (409)...
    if prestamo.fecha_devolucion is not None:
        raise Conflicto("El préstamo ya fue devuelto")
    # ...y la fecha no es anterior al prestamo (422).
    if datos.fecha_devolucion < prestamo.fecha_prestamo:
        raise ReglaNegocio("La fecha de devolución no puede ser anterior a la fecha del préstamo")

    # R10: si se devuelve tarde, multa = dias de retraso x 0.50
    dias_retraso = (datos.fecha_devolucion - prestamo.fecha_limite).days
    prestamo.fecha_devolucion = datos.fecha_devolucion
    prestamo.multa = MULTA_POR_DIA * max(0, dias_retraso)
    db.commit()
    return _recargar(db, prestamo)

"""Reportes: cada uno se resuelve con UNA sola consulta SQL (joins + agregados).

En PostgreSQL toda columna del SELECT que no sea un agregado debe aparecer en el
GROUP BY; por eso se agrupa por id y por nombre.
"""

from datetime import date

from sqlalchemy import Date, Integer, cast, func, literal, select
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session

from ..models import Autor, Categoria, Libro, Prestamo, Socio, libro_categoria


def libros_mas_prestados(db: Session, limite: int = 5) -> list[RowMapping]:
    """join + group_by + count + order_by."""
    total = func.count(Prestamo.id).label("total_prestamos")
    consulta = (
        select(Libro.id.label("libro_id"), Libro.titulo, Autor.nombre.label("autor"), total)
        .join(Autor, Libro.autor_id == Autor.id)
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .group_by(Libro.id, Libro.titulo, Autor.nombre)
        .order_by(total.desc(), Libro.titulo)
        .limit(limite)
    )
    return list(db.execute(consulta).mappings())


def libros_por_categoria(db: Session) -> list[RowMapping]:
    """outerjoin + group_by: aparecen tambien las categorias con 0 libros."""
    total = func.count(libro_categoria.c.libro_id).label("total_libros")
    consulta = (
        select(Categoria.id.label("categoria_id"), Categoria.nombre.label("categoria"), total)
        .outerjoin(libro_categoria, libro_categoria.c.categoria_id == Categoria.id)
        .group_by(Categoria.id, Categoria.nombre)
        .order_by(total.desc(), Categoria.nombre)
    )
    return list(db.execute(consulta).mappings())


def prestamos_vencidos(db: Session) -> list[RowMapping]:
    """join de 3 tablas (prestamos, libros, socios) + where."""
    hoy = cast(literal(date.today()), Date)
    # En PostgreSQL, fecha - fecha = numero de dias (entero).
    dias_retraso = cast(hoy - Prestamo.fecha_limite, Integer).label("dias_retraso")
    consulta = (
        select(
            Prestamo.id.label("prestamo_id"),
            Libro.titulo,
            Socio.nombre.label("socio"),
            Socio.email,
            Prestamo.fecha_limite,
            dias_retraso,
        )
        .join(Libro, Prestamo.libro_id == Libro.id)
        .join(Socio, Prestamo.socio_id == Socio.id)
        .where(Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite < hoy)
        .order_by(dias_retraso.desc(), Prestamo.id)
    )
    return list(db.execute(consulta).mappings())


def socios_con_multas(db: Session) -> list[RowMapping]:
    """group_by + sum + having: solo los socios cuya suma de multas es > 0."""
    total_multas = func.sum(Prestamo.multa).label("total_multas")
    con_multa = func.count(Prestamo.id).filter(Prestamo.multa > 0).label("prestamos_con_multa")
    consulta = (
        select(Socio.id.label("socio_id"), Socio.nombre, Socio.email, total_multas, con_multa)
        .join(Prestamo, Prestamo.socio_id == Socio.id)
        .group_by(Socio.id, Socio.nombre, Socio.email)
        .having(func.sum(Prestamo.multa) > 0)
        .order_by(total_multas.desc(), Socio.nombre)
    )
    return list(db.execute(consulta).mappings())


def resumen_autores(db: Session) -> list[RowMapping]:
    """outerjoin + count(distinct): libros, ejemplares y prestamos de cada autor.

    Si se hiciera autores -> libros -> prestamos y se sumaran los ejemplares,
    cada libro se repetiria una vez por prestamo y la suma saldria inflada.
    Por eso los prestamos se cuentan antes por libro en una subconsulta (sigue
    siendo una sola consulta SQL que PostgreSQL ejecuta de una vez).
    """
    prestamos_por_libro = (
        select(Prestamo.libro_id, func.count(Prestamo.id).label("total"))
        .group_by(Prestamo.libro_id)
        .subquery()
    )
    consulta = (
        select(
            Autor.id.label("autor_id"),
            Autor.nombre.label("autor"),
            func.count(func.distinct(Libro.id)).label("total_libros"),
            func.coalesce(func.sum(Libro.ejemplares), 0).label("total_ejemplares"),
            func.coalesce(func.sum(prestamos_por_libro.c.total), 0).label("total_prestamos"),
        )
        .outerjoin(Libro, Libro.autor_id == Autor.id)
        .outerjoin(prestamos_por_libro, prestamos_por_libro.c.libro_id == Libro.id)
        .group_by(Autor.id, Autor.nombre)
        .order_by(Autor.nombre)
    )
    return list(db.execute(consulta).mappings())


def resumen_general(db: Session) -> RowMapping:
    """Un solo SELECT con varias subconsultas escalares (func.count y func.sum)."""
    hoy = date.today()
    sin_devolver = Prestamo.fecha_devolucion.is_(None)

    def escalar(consulta):
        return consulta.scalar_subquery()

    consulta = select(
        escalar(select(func.count(Libro.id))).label("total_libros"),
        escalar(select(func.coalesce(func.sum(Libro.ejemplares), 0))).label("total_ejemplares"),
        escalar(select(func.count(Prestamo.id)).where(sin_devolver)).label("prestados"),
        escalar(select(func.count(Socio.id)).where(Socio.activo.is_(True))).label("socios_activos"),
        escalar(
            select(func.count(Prestamo.id)).where(sin_devolver, Prestamo.fecha_limite < hoy)
        ).label("prestamos_vencidos"),
        escalar(select(func.coalesce(func.sum(Prestamo.multa), 0))).label("total_multas"),
    )
    return db.execute(consulta).mappings().one()

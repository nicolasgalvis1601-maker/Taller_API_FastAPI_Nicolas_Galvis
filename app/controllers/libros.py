from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.dependencies import Paginacion
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models import Autor, Categoria, Libro, Prestamo
from ..schemas import LibroActualizar, LibroCrear, OrdenLibros
from . import autores as autores_ctrl
from . import categorias as categorias_ctrl
from ._comun import confirmar, patron_contiene

# Cada valor del Enum se traduce a un ORDER BY. Libro.id desempata para que la
# paginacion sea estable (sin repetir ni saltarse libros entre paginas).
ORDENES = {
    OrdenLibros.titulo: (Libro.titulo, Libro.id),
    OrdenLibros.anio: (Libro.anio_publicacion, Libro.id),
    OrdenLibros.anio_desc: (Libro.anio_publicacion.desc(), Libro.id),
}


def _consulta_base():
    # selectinload trae el autor y las categorias de TODOS los libros con una
    # consulta extra cada uno (y no una consulta por cada libro).
    return select(Libro).options(selectinload(Libro.autor), selectinload(Libro.categorias))


def listar(
    db: Session,
    pag: Paginacion,
    buscar: str | None = None,
    autor: str | None = None,
    categoria_id: int | None = None,
    desde: int | None = None,
    hasta: int | None = None,
    orden: OrdenLibros = OrdenLibros.titulo,
    autor_id: int | None = None,
) -> list[Libro]:
    if desde is not None and hasta is not None and desde > hasta:
        raise ReglaNegocio("'desde' no puede ser mayor que 'hasta'")

    # La consulta se construye poco a poco: cada filtro agrega su WHERE / JOIN.
    consulta = _consulta_base()
    if buscar and buscar.strip():
        consulta = consulta.where(Libro.titulo.ilike(patron_contiene(buscar), escape="\\"))
    if autor and autor.strip():
        consulta = consulta.join(Libro.autor).where(
            Autor.nombre.ilike(patron_contiene(autor), escape="\\")
        )
    if categoria_id is not None:
        # JOIN con la tabla intermedia libro_categoria y con categorias.
        consulta = consulta.join(Libro.categorias).where(Categoria.id == categoria_id)
    if desde is not None:
        consulta = consulta.where(Libro.anio_publicacion >= desde)
    if hasta is not None:
        consulta = consulta.where(Libro.anio_publicacion <= hasta)
    if autor_id is not None:
        consulta = consulta.where(Libro.autor_id == autor_id)

    consulta = consulta.order_by(*ORDENES[orden]).offset(pag.skip).limit(pag.limit)
    return list(db.scalars(consulta))


def listar_de_autor(db: Session, autor_id: int, pag: Paginacion) -> list[Libro]:
    autores_ctrl.obtener(db, autor_id)  # 404 si el autor no existe
    return listar(db, pag, autor_id=autor_id)


def obtener(db: Session, libro_id: int) -> Libro:
    libro = db.scalar(_consulta_base().where(Libro.id == libro_id))
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    return libro


def contar_prestamos_sin_devolver(db: Session, libro_id: int) -> int:
    return db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro_id, Prestamo.fecha_devolucion.is_(None)
        )
    )


def _validar_isbn_unico(db: Session, isbn: str, excluir_id: int | None = None) -> None:
    consulta = select(Libro.id).where(Libro.isbn == isbn)
    if excluir_id is not None:
        consulta = consulta.where(Libro.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe un libro con el ISBN {isbn}")


def _recargar(db: Session, libro: Libro) -> Libro:
    # expire + obtener: descarta lo que hay en memoria y lee lo que quedo guardado
    # en PostgreSQL (autor, categorias y disponibles actualizados).
    libro_id = libro.id
    db.expire(libro)
    return obtener(db, libro_id)


def crear(db: Session, datos: LibroCrear) -> Libro:
    autores_ctrl.obtener(db, datos.autor_id)  # 404
    categorias = categorias_ctrl.obtener_varias(db, datos.categoria_ids)  # 404
    _validar_isbn_unico(db, datos.isbn)  # 409

    libro = Libro(**datos.model_dump(exclude={"categoria_ids"}))
    libro.categorias = categorias  # SQLAlchemy llena libro_categoria
    db.add(libro)
    confirmar(db, f"Ya existe un libro con el ISBN {datos.isbn}")
    return _recargar(db, libro)


def actualizar(db: Session, libro_id: int, datos: LibroActualizar) -> Libro:
    libro = obtener(db, libro_id)
    # Los campos obligatorios enviados como null se ignoran.
    cambios = {k: v for k, v in datos.model_dump(exclude_unset=True).items() if v is not None}

    if "autor_id" in cambios:
        autores_ctrl.obtener(db, cambios["autor_id"])
    if "isbn" in cambios:
        _validar_isbn_unico(db, cambios["isbn"], excluir_id=libro_id)
    if "ejemplares" in cambios:
        prestados = contar_prestamos_sin_devolver(db, libro_id)
        if cambios["ejemplares"] < prestados:
            raise ReglaNegocio(
                f"El libro tiene {prestados} préstamo(s) sin devolver; "
                f"no puede quedar con {cambios['ejemplares']} ejemplar(es)"
            )
    if "categoria_ids" in cambios:
        # Reemplaza TODAS las categorias por las enviadas.
        libro.categorias = categorias_ctrl.obtener_varias(db, cambios.pop("categoria_ids"))

    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    confirmar(db, f"Ya existe un libro con el ISBN {cambios.get('isbn')}")
    return _recargar(db, libro)


def eliminar(db: Session, libro_id: int) -> None:
    libro = obtener(db, libro_id)
    sin_devolver = contar_prestamos_sin_devolver(db, libro_id)
    if sin_devolver:
        raise Conflicto(
            f"El libro tiene {sin_devolver} préstamo(s) sin devolver; no se puede eliminar"
        )
    # Se borran tambien sus filas de libro_categoria y su historial de prestamos devueltos.
    db.delete(libro)
    db.commit()

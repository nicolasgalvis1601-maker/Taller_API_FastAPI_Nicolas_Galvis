from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.dependencies import Paginacion
from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Categoria
from ..schemas import CategoriaActualizar, CategoriaCrear
from ._comun import confirmar


def listar(db: Session, pag: Paginacion) -> list[Categoria]:
    consulta = select(Categoria).order_by(Categoria.nombre).offset(pag.skip).limit(pag.limit)
    return list(db.scalars(consulta))


def obtener(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NoEncontrado("Categoría no encontrada")
    return categoria


def obtener_varias(db: Session, categoria_ids: list[int]) -> list[Categoria]:
    """Devuelve las categorias pedidas (en el mismo orden) o 404 si falta alguna."""
    encontradas = {c.id: c for c in db.scalars(select(Categoria).where(Categoria.id.in_(categoria_ids)))}
    faltantes = [i for i in categoria_ids if i not in encontradas]
    if faltantes:
        raise NoEncontrado(f"Categoría no encontrada: {', '.join(map(str, faltantes))}")
    return [encontradas[i] for i in categoria_ids]


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    # Los nombres ya llegan en minusculas desde el esquema.
    consulta = select(Categoria.id).where(func.lower(Categoria.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Categoria.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe la categoría '{nombre}'")


def crear(db: Session, datos: CategoriaCrear) -> Categoria:
    _validar_nombre_unico(db, datos.nombre)
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    confirmar(db, f"Ya existe la categoría '{datos.nombre}'")
    return categoria


def actualizar(db: Session, categoria_id: int, datos: CategoriaActualizar) -> Categoria:
    categoria = obtener(db, categoria_id)
    cambios = datos.model_dump(exclude_unset=True)
    if cambios.get("nombre") is None:
        cambios.pop("nombre", None)
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=categoria_id)
    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)
    confirmar(db, f"Ya existe la categoría '{cambios.get('nombre')}'")
    return categoria


def eliminar(db: Session, categoria_id: int) -> None:
    """Elimina la categoria y la quita de los libros que la tenian.

    SQLAlchemy borra primero sus filas de libro_categoria (y la FK con
    ON DELETE CASCADE lo garantiza tambien en PostgreSQL). Los libros no se tocan.
    """
    categoria = obtener(db, categoria_id)
    db.delete(categoria)
    db.commit()

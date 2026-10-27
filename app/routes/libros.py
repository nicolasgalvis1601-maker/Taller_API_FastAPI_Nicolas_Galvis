from fastapi import APIRouter, Query, Response, status

from ..controllers import libros as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..core.limites import MAX_INT, IdPath
from ..schemas import LibroActualizar, LibroCrear, LibroLeer, OrdenLibros

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("", response_model=list[LibroLeer])
def listar_libros(
    db: SessionDep,
    pag: PaginacionDep,
    buscar: str | None = Query(None, max_length=150, description="Texto contenido en el título"),
    autor: str | None = Query(None, max_length=100, description="Texto contenido en el nombre del autor"),
    categoria_id: int | None = Query(None, gt=0, le=MAX_INT),
    desde: int | None = Query(None, ge=0, le=9999, description="Año de publicación mínimo"),
    hasta: int | None = Query(None, ge=0, le=9999, description="Año de publicación máximo"),
    orden: OrdenLibros = Query(OrdenLibros.titulo, description="titulo, anio o -anio"),
):
    return controlador.listar(db, pag, buscar, autor, categoria_id, desde, hasta, orden)


@router.get("/{libro_id}", response_model=LibroLeer)
def obtener_libro(libro_id: IdPath, db: SessionDep):
    return controlador.obtener(db, libro_id)


@router.post("", response_model=LibroLeer, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{libro_id}", response_model=LibroLeer)
def actualizar_libro(libro_id: IdPath, datos: LibroActualizar, db: SessionDep):
    return controlador.actualizar(db, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: IdPath, db: SessionDep) -> Response:
    controlador.eliminar(db, libro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

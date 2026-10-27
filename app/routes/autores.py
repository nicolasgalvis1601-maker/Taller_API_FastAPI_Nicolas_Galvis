from fastapi import APIRouter, Query, Response, status

from ..controllers import autores as controlador
from ..controllers import libros as libros_ctrl
from ..core.dependencies import PaginacionDep, SessionDep
from ..core.limites import IdPath
from ..schemas import AutorActualizar, AutorCrear, AutorLeer, LibroLeer

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("", response_model=list[AutorLeer])
def listar_autores(
    db: SessionDep,
    pag: PaginacionDep,
    nacionalidad: str | None = Query(None, max_length=60, examples=["Colombiana"]),
):
    return controlador.listar(db, pag, nacionalidad)


@router.get("/{autor_id}", response_model=AutorLeer)
def obtener_autor(autor_id: IdPath, db: SessionDep):
    return controlador.obtener(db, autor_id)


@router.get("/{autor_id}/libros", response_model=list[LibroLeer])
def listar_libros_de_autor(autor_id: IdPath, db: SessionDep, pag: PaginacionDep):
    return libros_ctrl.listar_de_autor(db, autor_id, pag)


@router.post("", response_model=AutorLeer, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{autor_id}", response_model=AutorLeer)
def actualizar_autor(autor_id: IdPath, datos: AutorActualizar, db: SessionDep):
    return controlador.actualizar(db, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: IdPath, db: SessionDep) -> Response:
    controlador.eliminar(db, autor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

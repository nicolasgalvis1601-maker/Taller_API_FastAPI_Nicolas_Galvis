from fastapi import APIRouter, Response, status

from ..controllers import categorias as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..core.limites import IdPath
from ..schemas import CategoriaActualizar, CategoriaCrear, CategoriaLeer

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaLeer])
def listar_categorias(db: SessionDep, pag: PaginacionDep):
    return controlador.listar(db, pag)


@router.get("/{categoria_id}", response_model=CategoriaLeer)
def obtener_categoria(categoria_id: IdPath, db: SessionDep):
    return controlador.obtener(db, categoria_id)


@router.post("", response_model=CategoriaLeer, status_code=status.HTTP_201_CREATED)
def crear_categoria(datos: CategoriaCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{categoria_id}", response_model=CategoriaLeer)
def actualizar_categoria(categoria_id: IdPath, datos: CategoriaActualizar, db: SessionDep):
    return controlador.actualizar(db, categoria_id, datos)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: IdPath, db: SessionDep) -> Response:
    controlador.eliminar(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

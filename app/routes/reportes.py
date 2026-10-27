from fastapi import APIRouter, Query

from ..controllers import reportes as controlador
from ..core.dependencies import SessionDep
from ..schemas import (
    LibroMasPrestado,
    LibrosPorCategoria,
    PrestamoVencido,
    ResumenAutor,
    ResumenGeneral,
    SocioConMultas,
)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/libros-mas-prestados", response_model=list[LibroMasPrestado])
def libros_mas_prestados(db: SessionDep, limite: int = Query(5, ge=1, le=100)):
    return controlador.libros_mas_prestados(db, limite)


@router.get("/categorias", response_model=list[LibrosPorCategoria])
def libros_por_categoria(db: SessionDep):
    return controlador.libros_por_categoria(db)


@router.get("/prestamos-vencidos", response_model=list[PrestamoVencido])
def prestamos_vencidos(db: SessionDep):
    return controlador.prestamos_vencidos(db)


@router.get("/socios-con-multas", response_model=list[SocioConMultas])
def socios_con_multas(db: SessionDep):
    return controlador.socios_con_multas(db)


@router.get("/autores", response_model=list[ResumenAutor])
def resumen_autores(db: SessionDep):
    return controlador.resumen_autores(db)


@router.get("/resumen", response_model=ResumenGeneral)
def resumen_general(db: SessionDep):
    return controlador.resumen_general(db)

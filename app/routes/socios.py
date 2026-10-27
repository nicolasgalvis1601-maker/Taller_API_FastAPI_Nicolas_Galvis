from fastapi import APIRouter, Query, Response, status

from ..controllers import prestamos as prestamos_ctrl
from ..controllers import socios as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..core.limites import IdPath
from ..schemas import EstadoPrestamo, PrestamoLeer, SocioActualizar, SocioCrear, SocioLeer

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("", response_model=list[SocioLeer])
def listar_socios(db: SessionDep, pag: PaginacionDep, activo: bool | None = None):
    return controlador.listar(db, pag, activo)


@router.get("/{socio_id}", response_model=SocioLeer)
def obtener_socio(socio_id: IdPath, db: SessionDep):
    return controlador.obtener(db, socio_id)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoLeer])
def listar_prestamos_de_socio(
    socio_id: IdPath,
    db: SessionDep,
    pag: PaginacionDep,
    estado: EstadoPrestamo | None = Query(None, description="activo, vencido o devuelto"),
):
    return prestamos_ctrl.listar_de_socio(db, socio_id, pag, estado)


@router.post("", response_model=SocioLeer, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{socio_id}", response_model=SocioLeer)
def actualizar_socio(socio_id: IdPath, datos: SocioActualizar, db: SessionDep):
    return controlador.actualizar(db, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: IdPath, db: SessionDep) -> Response:
    """409 si tiene préstamos sin devolver; si solo tiene devueltos se desactiva;
    si no tiene préstamos, se elimina."""
    controlador.eliminar(db, socio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

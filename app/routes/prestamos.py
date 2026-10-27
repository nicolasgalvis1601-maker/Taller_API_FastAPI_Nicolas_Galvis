from fastapi import APIRouter, Body, Query, status

from ..controllers import prestamos as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..core.limites import MAX_INT, IdPath
from ..schemas import EstadoPrestamo, PrestamoCrear, PrestamoDevolucion, PrestamoLeer

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.get("", response_model=list[PrestamoLeer])
def listar_prestamos(
    db: SessionDep,
    pag: PaginacionDep,
    estado: EstadoPrestamo | None = Query(None, description="activo, vencido o devuelto"),
    socio_id: int | None = Query(None, gt=0, le=MAX_INT),
    libro_id: int | None = Query(None, gt=0, le=MAX_INT),
):
    return controlador.listar(db, pag, estado, socio_id, libro_id)


@router.get("/{prestamo_id}", response_model=PrestamoLeer)
def obtener_prestamo(prestamo_id: IdPath, db: SessionDep):
    return controlador.obtener(db, prestamo_id)


@router.post("", response_model=PrestamoLeer, status_code=status.HTTP_201_CREATED)
def crear_prestamo(datos: PrestamoCrear, db: SessionDep):
    """Aplica las reglas R1 a R8."""
    return controlador.crear(db, datos)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoLeer)
def devolver_prestamo(
    prestamo_id: IdPath,
    db: SessionDep,
    datos: PrestamoDevolucion | None = Body(None, description="Opcional. Sin cuerpo = hoy"),
):
    """Aplica las reglas R9 y R10. Responde 200 con la multa calculada."""
    return controlador.devolver(db, prestamo_id, datos or PrestamoDevolucion())

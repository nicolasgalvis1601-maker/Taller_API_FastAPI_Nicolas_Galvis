from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import models  # noqa: F401  (registra las tablas en Base.metadata)
from .core.database import Base, engine
from .core.exceptions import ErrorAplicacion
from .routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas que falten al arrancar (no modifica las que ya existen).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Biblioteca",
    description="Autores, categorías, libros, socios, préstamos y reportes (MVC + PostgreSQL)",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(api_router)


@app.exception_handler(ErrorAplicacion)
async def manejar_error_aplicacion(request: Request, exc: ErrorAplicacion) -> JSONResponse:
    """Unico manejador: cualquier excepcion propia responde { "detail": "mensaje" }."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})

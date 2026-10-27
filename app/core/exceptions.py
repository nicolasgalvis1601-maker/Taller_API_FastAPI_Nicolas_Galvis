"""Excepciones propias de la aplicacion.

Los controladores lanzan estas excepciones (nunca HTTPException) y el unico
exception_handler de main.py las convierte en { "detail": "mensaje" } con el
codigo HTTP que indica cada clase.
"""


class ErrorAplicacion(Exception):
    """Clase base de todas las excepciones propias."""

    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class NoEncontrado(ErrorAplicacion):
    """El recurso no existe."""

    status_code = 404


class Conflicto(ErrorAplicacion):
    """Datos duplicados, devolucion repetida o borrar algo con datos dependientes."""

    status_code = 409


class ReglaNegocio(ErrorAplicacion):
    """Una regla de la biblioteca no se cumple."""

    status_code = 422

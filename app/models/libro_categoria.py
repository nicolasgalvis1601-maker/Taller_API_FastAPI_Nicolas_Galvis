from sqlalchemy import Column, ForeignKey, Table

from ..core.database import Base

# Tabla intermedia de la relacion muchos a muchos libros <-> categorias.
# No necesita una clase propia porque solo guarda las dos claves foraneas.
# ON DELETE CASCADE: al borrar un libro o una categoria se borran sus filas aqui,
# asi la categoria "se quita de los libros que la tenian".
libro_categoria = Table(
    "libro_categoria",
    Base.metadata,
    Column("libro_id", ForeignKey("libros.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "categoria_id", ForeignKey("categorias.id", ondelete="CASCADE"), primary_key=True, index=True
    ),
)

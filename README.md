# Taller API REST con FastAPI y PostgreSQL — Biblioteca

Backend del sistema de préstamos de una biblioteca: **autores**, **categorías**, **libros**,
**socios**, **préstamos** (con reglas de negocio y multas) y **reportes** con joins y funciones
de agregado. Construido con Python, FastAPI, SQLAlchemy 2, Pydantic 2 y PostgreSQL, organizado
con el patrón **MVC**.

## Integrantes

| Nombre | Programa |
|--------|----------|
| _Tu nombre y apellido_ | Tecnólogo en Análisis y Desarrollo de Software — SENA |

## Relaciones

```
autores 1 ──── N libros N ──── M categorias      (tabla intermedia libro_categoria)
                   1
                   │
                   N
socios  1 ──── N prestamos
```

- `libros.autor_id` → `autores.id` (RESTRICT: no se borra un autor con libros).
- `libro_categoria (libro_id, categoria_id)` → ON DELETE CASCADE en ambos lados.
- `prestamos.socio_id` → `socios.id` (RESTRICT) y `prestamos.libro_id` → `libros.id`.

## Estructura

```
biblioteca/
├── app/
│   ├── main.py              # crea la app, registra routers y el único exception_handler
│   ├── core/
│   │   ├── database.py      # engine, SessionLocal y Base (lee DATABASE_URL de .env)
│   │   ├── dependencies.py  # get_db / SessionDep y la paginación (PaginacionDep)
│   │   ├── exceptions.py    # ErrorAplicacion 400, NoEncontrado 404, Conflicto 409, ReglaNegocio 422
│   │   └── limites.py       # MAX_INT e IdPath (ids que caben en INTEGER)
│   ├── models/              # tablas SQLAlchemy y sus relaciones
│   │   ├── autor.py  categoria.py  libro.py  libro_categoria.py  socio.py  prestamo.py
│   ├── schemas/             # validación de entrada y forma de las respuestas (Pydantic)
│   │   ├── autor.py  categoria.py  libro.py  socio.py  prestamo.py  reporte.py  _comun.py
│   ├── controllers/         # consultas y reglas de negocio (sin nada de HTTP)
│   │   ├── autores.py  categorias.py  libros.py  socios.py  prestamos.py  reportes.py  _comun.py
│   └── routes/              # endpoints: reciben la petición y llaman al controlador
│       ├── autores.py  categorias.py  libros.py  socios.py  prestamos.py  reportes.py
├── tests/                   # pruebas automáticas con pytest (los 24 casos + reglas R1–R10)
├── .env.example  .gitignore  docker-compose.yml
├── requirements.txt  requirements-dev.txt
└── README.md
```

**Cómo viaja una petición:** `routes` (valida con `schemas`) → `controllers` (consultas con
`models` y reglas de negocio; lanza excepciones propias) → `routes` responde con el
`response_model`. Si el controlador lanza una excepción propia, el manejador de `main.py`
responde `{ "detail": "mensaje" }` con su código.

## Instalación

Requisitos: Python 3.11 o superior y PostgreSQL.

1. **Base de datos.** Crea una base vacía en PostgreSQL:

   ```sql
   CREATE DATABASE biblioteca;
   ```

   O, si tienes Docker: `docker compose up -d` (usuario, clave y base: `biblioteca`).

2. **Entorno virtual y dependencias** (desde la carpeta del proyecto):

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1        # Windows (PowerShell)
   # source .venv/bin/activate       # Linux / macOS
   pip install -r requirements.txt
   ```

## Variables de entorno

Copia `.env.example` como `.env` y ajusta la conexión:

| Variable | Ejemplo | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+psycopg://postgres:clave@localhost:5432/biblioteca` | Conexión a PostgreSQL con el driver psycopg 3 |
| `TEST_DATABASE_URL` | `postgresql+psycopg://postgres:clave@localhost:5432/biblioteca_test` | Solo para `pytest`. **Otra base**: las pruebas borran las tablas |

Si `DATABASE_URL` comienza con `//` y contiene el host, puerto y nombre de la base,
la aplicación agrega automáticamente el esquema `postgresql+psycopg:`. Así no es necesario
modificar un `.env` existente con ese formato.

## Cómo ejecutar

```powershell
uvicorn app.main:app --reload
```

- Swagger: <http://127.0.0.1:8000/docs>
- Las tablas se crean solas al arrancar (`Base.metadata.create_all`).

## Endpoints

Todos los listados aceptan `skip` (≥ 0, por defecto 0) y `limit` (1 a 100, por defecto 20).

### Autores

| Método | Ruta | Descripción | Respuestas |
|--------|------|-------------|------------|
| `GET` | `/autores` | Lista paginada. Filtro `?nacionalidad=` | 200 |
| `GET` | `/autores/{id}` | Un autor | 200 / 404 |
| `GET` | `/autores/{id}/libros` | Libros del autor | 200 / 404 |
| `POST` | `/autores` | Crea (409 si el nombre ya existe) | 201 / 409 / 422 |
| `PATCH` | `/autores/{id}` | Actualiza solo los campos enviados | 200 / 404 / 409 / 422 |
| `DELETE` | `/autores/{id}` | Elimina (409 si tiene libros) | 204 / 404 / 409 |

### Categorías

| Método | Ruta | Descripción | Respuestas |
|--------|------|-------------|------------|
| `GET` | `/categorias` | Lista paginada | 200 |
| `GET` | `/categorias/{id}` | Una categoría | 200 / 404 |
| `POST` | `/categorias` | Crea (se guarda en minúsculas; 409 si ya existe) | 201 / 409 / 422 |
| `PATCH` | `/categorias/{id}` | Actualiza | 200 / 404 / 409 / 422 |
| `DELETE` | `/categorias/{id}` | Elimina y la quita de los libros que la tenían | 204 / 404 |

### Libros

| Método | Ruta | Descripción | Respuestas |
|--------|------|-------------|------------|
| `GET` | `/libros` | Lista paginada con filtros combinables (ver abajo) | 200 / 422 |
| `GET` | `/libros/{id}` | Libro con autor, categorías y `disponibles` | 200 / 404 |
| `POST` | `/libros` | Crea (404 autor/categoría inexistente; 409 ISBN repetido) | 201 / 404 / 409 / 422 |
| `PATCH` | `/libros/{id}` | Actualiza; `categoria_ids` reemplaza las categorías. 422 si `ejemplares` queda por debajo de los préstamos activos | 200 / 404 / 409 / 422 |
| `DELETE` | `/libros/{id}` | Elimina (409 si tiene préstamos sin devolver) | 204 / 404 / 409 |

Filtros de `GET /libros`: `buscar` (título, ilike), `autor` (nombre del autor, join),
`categoria_id` (join con la tabla intermedia), `desde` / `hasta` (año de publicación) y
`orden` = `titulo` | `anio` | `-anio` (Enum).

### Socios

| Método | Ruta | Descripción | Respuestas |
|--------|------|-------------|------------|
| `GET` | `/socios` | Lista paginada. Filtro `?activo=true/false` | 200 |
| `GET` | `/socios/{id}` | Un socio | 200 / 404 |
| `GET` | `/socios/{id}/prestamos` | Préstamos del socio. Filtro `?estado=activo\|vencido\|devuelto` | 200 / 404 |
| `POST` | `/socios` | Crea (email en minúsculas; 409 si ya existe) | 201 / 409 / 422 |
| `PATCH` | `/socios/{id}` | Actualiza (también permite reactivar con `"activo": true`) | 200 / 404 / 409 / 422 |
| `DELETE` | `/socios/{id}` | 409 si tiene préstamos sin devolver; si solo tiene devueltos se desactiva; si no tiene, se elimina | 204 / 404 / 409 |

### Préstamos

| Método | Ruta | Descripción | Respuestas |
|--------|------|-------------|------------|
| `GET` | `/prestamos` | Lista paginada. Filtros `?estado=`, `?socio_id=`, `?libro_id=` | 200 |
| `GET` | `/prestamos/{id}` | Préstamo con el libro y el socio anidados | 200 / 404 |
| `POST` | `/prestamos` | Registra un préstamo (reglas R1 a R8) | 201 / 404 / 409 / 422 |
| `POST` | `/prestamos/{id}/devolucion` | Registra la devolución (R9 y R10). Cuerpo opcional; sin cuerpo = hoy | 200 / 404 / 409 / 422 |

### Reportes (cada uno es una sola consulta SQL)

| Ruta | Devuelve | Técnica |
|------|----------|---------|
| `GET /reportes/libros-mas-prestados?limite=5` | Libro, autor y total de préstamos, de mayor a menor | join + group_by + count + order_by |
| `GET /reportes/categorias` | Total de libros por categoría, incluidas las que tienen 0 | outerjoin + group_by |
| `GET /reportes/prestamos-vencidos` | Préstamo, título, socio, email, fecha límite y días de retraso | join de 3 tablas + where |
| `GET /reportes/socios-con-multas` | Socio, total de multas y préstamos con multa | group_by + sum + having |
| `GET /reportes/autores` | Libros, ejemplares y préstamos de cada autor | outerjoin + count(distinct) |
| `GET /reportes/resumen` | Totales: libros, ejemplares, prestados, socios activos, vencidos y multas | select(func.count()) y func.sum |

## Reglas de negocio de préstamos

El estado **no se guarda**: se calcula con las fechas (`devuelto` si tiene `fecha_devolucion`;
`vencido` si no se ha devuelto y `fecha_limite` < hoy; si no, `activo`).

| Regla | Descripción | Si no se cumple |
|-------|-------------|-----------------|
| R1 | El socio existe | 404 |
| R2 | El libro existe | 404 |
| R3 | El socio está activo | 422 "El socio no está activo" |
| R4 | El socio no tiene préstamos vencidos | 422 "El socio tiene préstamos vencidos" |
| R5 | El socio tiene menos de 3 préstamos sin devolver | 422 "Máximo de 3 préstamos" |
| R6 | El socio no tiene ya ese mismo libro sin devolver | 409 |
| R7 | El libro tiene ejemplares disponibles | 422 "No hay ejemplares disponibles" |
| R8 | `fecha_limite = fecha_prestamo + dias` (dias 1 a 30, por defecto 14) | — |
| R9 | Al devolver: el préstamo existe, no fue devuelto antes y la fecha no es anterior al préstamo | 404 / 409 / 422 |
| R10 | Si se devuelve tarde: `multa = días de retraso × 0,50` | — |

Además, al crear un préstamo se bloquean (`SELECT ... FOR UPDATE`) las filas del socio y del
libro, para que dos peticiones simultáneas no presten el mismo último ejemplar.

## Pruebas (Fase 7)

### Automáticas (pytest)

Ejecutan los 24 casos del taller y una prueba de cada regla R1–R10 sobre una base **de pruebas**:

```powershell
pip install -r requirements-dev.txt
# crea antes una base vacía: CREATE DATABASE biblioteca_test;
$env:TEST_DATABASE_URL="postgresql+psycopg://postgres:clave@localhost:5432/biblioteca_test"
pytest -v
```

### Manuales desde `/docs`

Con la base vacía, carga los datos en este orden:

```json
POST /autores
{ "nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana", "anio_nacimiento": 1927 }
{ "nombre": "Isabel Allende", "nacionalidad": "Chilena", "anio_nacimiento": 1942 }
{ "nombre": "George Orwell", "nacionalidad": "Británica", "anio_nacimiento": 1903 }

POST /categorias
{ "nombre": "Novela" }   { "nombre": "Realismo Mágico" }   { "nombre": "Distopía" }   { "nombre": "Poesía" }

POST /libros
{ "titulo": "Cien años de soledad", "isbn": "9780307474728", "anio_publicacion": 1967, "ejemplares": 2, "autor_id": 1, "categoria_ids": [1, 2] }
{ "titulo": "El amor en los tiempos del cólera", "isbn": "9780307387264", "anio_publicacion": 1985, "ejemplares": 1, "autor_id": 1, "categoria_ids": [1] }
{ "titulo": "La casa de los espíritus", "isbn": "9788401242267", "anio_publicacion": 1982, "ejemplares": 2, "autor_id": 2, "categoria_ids": [1, 2] }
{ "titulo": "1984", "isbn": "9780451524935", "anio_publicacion": 1949, "ejemplares": 3, "autor_id": 3, "categoria_ids": [1, 3] }

POST /socios
{ "nombre": "Ana Torres", "email": "ANA@example.com" }
{ "nombre": "Luis Pérez", "email": "luis@example.com" }
{ "nombre": "Marta Ruiz", "email": "marta@example.com" }
```

| # | Petición | Resultado esperado |
|---|----------|--------------------|
| 1 | `POST /autores` `{ "nombre": "Gabriel García Márquez" }` | 409 |
| 2 | `POST /libros` con `"isbn": "123"` | 422 |
| 3 | `POST /libros` con `"categoria_ids": [1, 1]` | 422 |
| 4 | `POST /libros` con `"autor_id": 99` | 404 |
| 5 | `GET /libros?categoria_id=2&orden=-anio` | La Casa De Los Espíritus (1982) y luego Cien Años De Soledad (1967) |
| 6 | `GET /libros?autor=gabriel` | Los 2 libros de García Márquez |
| 7 | `POST /prestamos` `{ "libro_id": 2, "socio_id": 1 }` | 201, `"estado": "activo"` |
| 8 | `POST /prestamos` `{ "libro_id": 2, "socio_id": 2 }` | 422 "No hay ejemplares disponibles" |
| 9 | `GET /libros/2` | `"disponibles": 0` |
| 10 | `POST /prestamos` `{ "libro_id": 1, "socio_id": 2, "fecha_prestamo": "<hoy − 20 días>", "dias": 7 }` | 201, `"estado": "vencido"` |
| 11 | `POST /prestamos` `{ "libro_id": 4, "socio_id": 2 }` | 422 "El socio tiene préstamos vencidos" |
| 12 | `GET /reportes/prestamos-vencidos` | El préstamo del caso 10 con `"dias_retraso": 13` |
| 13 | `POST /prestamos/2/devolucion` (sin cuerpo) | 200, `"multa": 6.5` |
| 14 | `POST /prestamos/2/devolucion` otra vez | 409 |
| 15 | `POST /prestamos` socio 3 con libros 1, 3 y 4; luego `{ "libro_id": 2, "socio_id": 3 }` | El cuarto: 422 "Máximo de 3 préstamos" |
| 16 | `PATCH /libros/4` `{ "ejemplares": 0 }` | 422 |
| 17 | `DELETE /autores/1` | 409 |
| 18 | `DELETE /libros/2` | 409 |
| 19 | `DELETE /socios/2` y luego `GET /socios/2` | 204 y `"activo": false` |
| 20 | `POST /prestamos` `{ "libro_id": 4, "socio_id": 2 }` | 422 "El socio no está activo" |
| 21 | `GET /reportes/categorias` | `poesía` con `"total_libros": 0` |
| 22 | `GET /reportes/socios-con-multas` | Solo Luis Pérez, `"total_multas": 6.5` |
| 23 | `GET /reportes/libros-mas-prestados?limite=3` | 3 libros de mayor a menor |
| 24 | `GET /libros?skip=0&limit=2` y `?skip=2&limit=2` | 2 libros en cada página, sin repetir |

> En el caso 10, `fecha_prestamo` es la fecha de hace 20 días en formato `AAAA-MM-DD`.
> En los casos 13 y 14 el id es el del préstamo creado en el caso 10 (el 2 si seguiste el orden).

## Formato de respuestas

```jsonc
// éxito (GET /libros/1)
{ "id": 1, "titulo": "Cien Años De Soledad", "isbn": "9780307474728", "anio_publicacion": 1967,
  "ejemplares": 2, "disponibles": 2,
  "autor": { "id": 1, "nombre": "Gabriel García Márquez" },
  "categorias": [ { "id": 1, "nombre": "novela" }, { "id": 2, "nombre": "realismo mágico" } ] }

// error propio
{ "detail": "Libro no encontrado" }

// error de validación (Pydantic)
{ "detail": [ { "loc": ["body", "isbn"], "msg": "String should match pattern '^[0-9]{13}$'", "...": "..." } ] }
```

| Código | Cuándo |
|--------|--------|
| 200 | Consulta o actualización correcta |
| 201 | Recurso creado |
| 204 | Recurso eliminado (sin cuerpo) |
| 404 | El recurso no existe |
| 409 | Datos duplicados, devolución repetida o borrar algo con datos dependientes |
| 422 | Error de validación de Pydantic o regla de negocio no cumplida |

## Decisiones de diseño

- **Validaciones** (`schemas/`): los textos se limpian con `field_validator(mode="before")`
  antes de comprobar su longitud. Autor, libro y socio en formato título; categorías y emails
  en minúsculas. El año máximo es el año actual, calculado en cada petición.
- **`disponibles`** no es una columna: `Libro.prestados` es un `column_property` (subconsulta
  que cuenta los préstamos sin devolver) y `disponibles = ejemplares − prestados`.
- **Unicidad**: se comprueba antes de insertar (409 con mensaje claro) y además la base tiene
  restricciones `UNIQUE`; si dos peticiones chocan a la vez, `confirmar()` convierte el
  `IntegrityError` en 409 en lugar de un 500.
- **Borrar un libro** sin préstamos pendientes borra también su historial de préstamos devueltos.
- **Paginación estable**: todos los listados se ordenan con un desempate por `id`, así las
  páginas no repiten ni saltan registros.

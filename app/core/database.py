import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL. Copia .env.example como .env y configura PostgreSQL.")

if DATABASE_URL.startswith("//"):
    DATABASE_URL = f"postgresql+psycopg:{DATABASE_URL}"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)


class Base(DeclarativeBase):
    pass

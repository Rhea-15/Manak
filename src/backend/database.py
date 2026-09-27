from sqlalchemy import create_engine  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import declarative_base, sessionmaker  # pyright: ignore[reportMissingImports]

DATABASE_URL = "postgresql+psycopg://manak:manak_password@localhost:5432/manak"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
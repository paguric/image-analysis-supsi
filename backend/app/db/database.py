from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.bootstrapper import get_db_path

# Using check_same_thread=False allows FastAPI to use the same SQLite database in different threads
connect_args = {"check_same_thread": False}

engine = create_engine(f"sqlite:///{get_db_path()}", connect_args=connect_args)


def reset_engine():
    """Dispone tutte le connessioni del pool e ricrea l'engine sul db attuale."""
    global engine
    engine.dispose()
    engine = create_engine(f"sqlite:///{get_db_path()}", connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
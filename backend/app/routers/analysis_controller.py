import os

from app.db import database

from fastapi import APIRouter


router = APIRouter(prefix="/analysis")


@router.delete("/reset/")
async def reset_db():
    """
    Rimuove il file del db attualmente in uso e ne ricrea uno vuoto.
    """

    # TODO split di questo endpoint in due per rispetto principio Single responsibility:
    #   - Rimozione db
    #   - Creazione nuovo db

    db_path = database.get_db_path()

    # Rimozione db vecchio
    if os.path.isfile(db_path):
        os.remove(db_path)
        print(f"{db_path} è stato eliminato con successo")
    else:
        print(f"Nessun db trovato in {db_path}. Non è possibile completare reset")
        # TODO raise Exception

    # Creazione nuovo db vuoto
    database.create_db_and_tables()

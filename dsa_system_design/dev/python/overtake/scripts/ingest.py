"""Ingest script: (re)build the vector index for every user's notes.

Usage:
    uv run python -m scripts.ingest

Runs against the configured database. Safe to run repeatedly (idempotent).
"""

from __future__ import annotations

from sqlmodel import Session, select

from app.ai.rag.retriever import Retriever
from app.core.logging import get_logger, setup_logging
from app.infra.db import Note, get_engine, init_db

_log = get_logger("overtake.ingest")


def main() -> None:
    setup_logging()
    init_db()
    retriever = Retriever()
    total_notes = 0
    total_chunks = 0
    with Session(get_engine()) as session:
        notes = session.exec(select(Note)).all()
        for note in notes:
            assert note.id is not None  # PK is populated once the row is persisted
            total_chunks += retriever.index_note(
                user_id=note.user_id,
                note_id=note.id,
                title=note.title,
                content=note.content,
            )
            total_notes += 1
    _log.info(
        "ingest complete",
        extra={"extra_fields": {"notes": total_notes, "chunks": total_chunks}},
    )
    print(f"Indexed {total_notes} notes into {total_chunks} chunks.")


if __name__ == "__main__":
    main()

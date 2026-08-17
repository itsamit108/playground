# Migrations

This app does not use a relational database by default (job state is in-memory,
RAG uses an in-memory vector store). If you add persistence via
`app/infra/db.py`, initialize Alembic here:

```bash
uv add alembic
uv run alembic init migrations
```

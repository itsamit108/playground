# FastAPI Cloud Demo

This demo FastAPI app starts a background task when the server starts and increments an in-memory counter once per second.

Endpoints:

- `GET /` shows the current counter.
- `GET /health` returns a health payload with the current counter.
- `GET /counter` returns the current count.
- `GET /specs` returns runtime system specs, including CPU, RAM, disk, OS, Python, container, and best-effort GPU details.
- `GET /docs` shows the generated FastAPI API docs.

Important: the counter is intentionally in memory for a simple cloud runtime demo. It resets when the instance restarts, when the app scales to zero, or when traffic is routed to a different instance.

## Local Run

```powershell
uv run fastapi dev
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
http://127.0.0.1:8000/counter
http://127.0.0.1:8000/specs
```

## Deploy to FastAPI Cloud

```powershell
uv run fastapi deploy
```

After deployment, use the URL printed by the CLI:

```text
https://your-app.fastapicloud.dev/docs
https://your-app.fastapicloud.dev/health
https://your-app.fastapicloud.dev/counter
https://your-app.fastapicloud.dev/specs
```

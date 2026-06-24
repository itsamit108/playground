"""Conversion service — the flagship PDF -> EPUB3 use case.

Drives the ``EpubConversionAgent`` workflow and tracks async job state. Routers
call this; they never touch the agent, the parser, or the EPUB writer directly.
"""

from __future__ import annotations

import threading
import uuid
from pathlib import Path

from app.ai.agents.state import RunState
from app.ai.agents.workflows import EpubConversionAgent
from app.ai.models.base import LLMClient
from app.core.config import Settings
from app.core.logging import get_logger
from app.infra import storage
from app.schemas.agents import AgentStep, ConversionStatusResponse

logger = get_logger(__name__)


class _JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str) -> None:
        with self._lock:
            self._jobs[job_id] = {"status": "processing", "output_path": None, "error": None, "steps": []}

    def update(self, job_id: str, **fields) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(fields)

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None


_store = _JobStore()


class ConversionService:
    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm = llm
        self.settings = settings

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        _store.create(job_id)
        return job_id

    def output_path_for(self, job_id: str) -> Path:
        return storage.output_dir(self.settings.output_dir) / f"{job_id}.epub"

    async def run(self, job_id: str, pdf_path: Path, output_path: Path, page_range: str | None) -> None:
        """Execute the conversion agent and update job state. Cleans up the
        uploaded temp PDF afterwards."""
        try:
            agent = EpubConversionAgent(self.llm, self.settings)
            state: RunState = await agent.run(
                goal="Convert PDF to EPUB3",
                inputs={
                    "pdf_path": str(pdf_path),
                    "output_path": str(output_path),
                    "page_range": page_range,
                },
            )
            steps = [
                {"name": s.name, "status": s.status.value, "detail": s.detail} for s in state.steps
            ]
            if state.failed:
                err = next((s.detail for s in state.steps if s.status.value == "error"), "conversion failed")
                _store.update(job_id, status="error", error=err, steps=steps)
                logger.error("Job %s failed: %s", job_id, err)
            else:
                _store.update(
                    job_id,
                    status="done",
                    output_path=state.output.get("output_path", str(output_path)),
                    steps=steps,
                )
                logger.info("Job %s completed: %s", job_id, output_path)
        except Exception as exc:  # pragma: no cover - defensive
            _store.update(job_id, status="error", error=str(exc))
            logger.exception("Job %s crashed", job_id)
        finally:
            try:
                Path(pdf_path).unlink(missing_ok=True)
            except OSError:
                pass

    def status(self, job_id: str) -> ConversionStatusResponse | None:
        job = _store.get(job_id)
        if not job:
            return None
        steps = [AgentStep(**s) for s in job.get("steps", [])]
        download_url = f"{self.settings.api_v1_prefix}/agents/convert/{job_id}/download" if job["status"] == "done" else None
        return ConversionStatusResponse(
            job_id=job_id,
            status=job["status"],
            download_url=download_url,
            error=job.get("error"),
            steps=steps,
        )

    def download_path(self, job_id: str) -> Path | None:
        job = _store.get(job_id)
        if not job or job["status"] != "done" or not job.get("output_path"):
            return None
        p = Path(job["output_path"])
        return p if p.exists() else None

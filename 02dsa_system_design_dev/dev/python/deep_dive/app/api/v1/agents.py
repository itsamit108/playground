"""Agent endpoints -> agent_service / conversion_service.

Hosts the generic agent-run endpoint AND the flagship PDF -> EPUB conversion,
which is implemented as an agent workflow.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.deps import AgentServiceDep, ConversionServiceDep, require_auth
from app.schemas.agents import (
    AgentRunRequest,
    AgentRunResponse,
    ConversionStart,
    ConversionStatusResponse,
)

router = APIRouter(prefix="/agents", tags=["agents"], dependencies=[Depends(require_auth)])


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(req: AgentRunRequest, service: AgentServiceDep) -> AgentRunResponse:
    return await service.run(req)


@router.post("/convert", response_model=ConversionStart, status_code=202)
async def start_conversion(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: ConversionServiceDep,
    pages: str | None = None,
) -> ConversionStart:
    """Upload a PDF and start an async PDF -> EPUB3 conversion (agent workflow).

    `pages`: optional page range, e.g. ?pages=1-3 or ?pages=1,5,9.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    job_id = service.create_job()

    suffix = Path(file.filename).suffix or ".pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(await file.read())
    tmp.close()
    pdf_path = Path(tmp.name)
    output_path = service.output_path_for(job_id)

    background_tasks.add_task(service.run, job_id, pdf_path, output_path, pages)
    return ConversionStart(job_id=job_id, status="processing")


@router.get("/convert/{job_id}", response_model=ConversionStatusResponse)
async def conversion_status(job_id: str, service: ConversionServiceDep) -> ConversionStatusResponse:
    status = service.status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return status


@router.get("/convert/{job_id}/download")
async def download_epub(job_id: str, service: ConversionServiceDep):
    status = service.status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if status.status != "done":
        raise HTTPException(status_code=409, detail=f"Job status is '{status.status}', not done.")
    path = service.download_path(job_id)
    if path is None:
        raise HTTPException(status_code=500, detail="Output file missing.")
    return FileResponse(
        path=str(path),
        media_type="application/epub+zip",
        filename=path.name,
    )

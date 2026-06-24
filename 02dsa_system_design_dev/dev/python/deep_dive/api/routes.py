import asyncio
import logging
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile
from fastapi.responses import FileResponse

from application.convert_use_case import convert

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory job store: job_id → {"status", "output_path", "error"}
_jobs: dict[str, dict] = {}

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/convert")
async def start_conversion(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    pages: str | None = None,
):
    """
    Upload a PDF file and start an async conversion job.

    Query param `pages`: optional page range, e.g. ?pages=1-3 or ?pages=1,5,9
    Returns a job_id to poll for status.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "processing", "output_path": None, "error": None}

    suffix = Path(file.filename).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(await file.read())
    tmp.close()
    pdf_path = Path(tmp.name)

    output_path = OUTPUT_DIR / f"{job_id}.epub"

    background_tasks.add_task(_run_conversion, job_id, pdf_path, output_path, pages)
    return {"job_id": job_id, "status": "processing"}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Poll conversion status."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    resp = {"job_id": job_id, "status": job["status"]}
    if job["status"] == "done":
        resp["download_url"] = f"/download/{job_id}"
    if job["status"] == "error":
        resp["error"] = job["error"]
    return resp


@router.get("/download/{job_id}")
async def download_epub(job_id: str):
    """Stream the generated EPUB file."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job["status"] != "done":
        raise HTTPException(status_code=409, detail=f"Job status is '{job['status']}', not done.")
    output_path = Path(job["output_path"])
    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Output file missing.")
    return FileResponse(
        path=str(output_path),
        media_type="application/epub+zip",
        filename=output_path.name,
    )


async def _run_conversion(job_id: str, pdf_path: Path, output_path: Path, page_range: str | None = None) -> None:
    try:
        result = await convert(pdf_path, output_path, page_range)
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["output_path"] = str(result)
        logger.info("Job %s completed: %s", job_id, result)
    except Exception as exc:
        _jobs[job_id]["status"] = "error"
        _jobs[job_id]["error"] = str(exc)
        logger.exception("Job %s failed", job_id)
    finally:
        # Clean up uploaded PDF temp file
        try:
            pdf_path.unlink(missing_ok=True)
        except Exception:
            pass

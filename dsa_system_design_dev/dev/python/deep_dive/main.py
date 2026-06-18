import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from api.routes import router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="PDF to EPUB Converter",
    description="Upload a PDF, get a professional EPUB3 back.",
    version="1.0.0",
)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""FastAPI web server for ContentGoldmine MVP.

Run: uvicorn main:app --reload
Then open http://localhost:8000
"""
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.pipeline import scan

app = FastAPI(title="ContentGoldmine MVP")


class ScanRequest(BaseModel):
    niche: str


@app.post("/api/scan")
def api_scan(req: ScanRequest):
    return scan(req.niche)


@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "frontend", "index.html"))

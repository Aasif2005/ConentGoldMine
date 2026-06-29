"""Controller wiring: FastAPI routes that delegate to controllers."""
import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.models.schemas import ScanRequest, ScanReport
from app.controllers.scan_controller import ScanController

router = APIRouter()
_controller = ScanController()

# routes.py lives in backend/app/ ; the frontend folder is a sibling of backend/.
# backend/app -> backend -> project root -> frontend
FRONTEND = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)


@router.post("/api/scan", response_model=ScanReport)
def scan(req: ScanRequest):
    """Analyze a niche and return ranked topics, videos, and communities."""
    return _controller.scan(req.niche)


@router.get("/")
def index():
    """Serve the niche search page."""
    return FileResponse(os.path.join(FRONTEND, "search.html"))


@router.get("/landing")
def landing():
    """Serve the marketing landing page if present, else the search page."""
    path = os.path.join(FRONTEND, "landing.html")
    if os.path.exists(path):
        return FileResponse(path)
    return FileResponse(os.path.join(FRONTEND, "search.html"))

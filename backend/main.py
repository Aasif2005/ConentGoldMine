"""ContentGoldmine MVP - application entrypoint (MVC).

Layout:
  app/models/       data + data sources (config, schemas, cache, youtube, reddit)
  app/services/     business logic (analyzer)
  app/controllers/  orchestration (scan_controller)
  app/views/        response shaping (serializers); frontend pages live in frontend/
  app/routes.py     HTTP routes (controller wiring)

Run:
  uvicorn main:app --reload    ->  http://localhost:8000
"""
from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="ContentGoldmine MVP", version="0.2.0")
app.include_router(router)

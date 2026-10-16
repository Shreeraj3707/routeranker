"""
RouteRanker API — FastAPI backend.
Run:  uvicorn backend.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.model_loader import bundle
from backend.routers import routes, predict, admin
from backend.db import engine, Base
from backend import orm_models  # ensures models are registered

app = FastAPI(
    title="RouteRanker API",
    description="AI-powered public transit route optimization backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    # Create tables if they don't exist (idempotent)
    Base.metadata.create_all(bind=engine)
    print("[startup] DB tables ensured")

    try:
        bundle.load()
        print("[startup] models loaded successfully")
    except Exception as e:
        print(f"[startup] WARNING: models not loaded — {e}")


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "RouteRanker API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/health", "/routes", "/predict"],
    }


@app.get("/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "models_loaded": bundle._loaded,
    }


app.include_router(routes.router)
app.include_router(predict.router)
app.include_router(admin.router)

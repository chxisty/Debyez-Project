"""
Aegis Knowledge System - FastAPI Application Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import router

app = FastAPI(
    title="Aegis Series-7 Knowledge & Evidence Engine",
    description=(
        "Production REST API for the Aegis Series-7 Hydraulic Control System (HCS). "
        "Provides evidence-grounded QA, multi-channel hybrid retrieval, revision-aware conflict resolution, "
        "cryptographic document provenance, and epistemic abstention detection."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development / production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)

# Mount raw diagrams and images if available
raw_data_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "raw"
)
if os.path.exists(raw_data_dir):
    app.mount("/static/raw", StaticFiles(directory=raw_data_dir), name="raw_static")

@app.get("/", tags=["Root"])
def root():
    return {
        "system": "Aegis Series-7 Hydraulic Control System (HCS)",
        "service": "Aegis Knowledge & Evidence Engine API",
        "documentation": "/docs",
        "health": "/health",
        "chat_endpoint": "/api/chat"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)


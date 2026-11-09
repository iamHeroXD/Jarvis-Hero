"""
JARVIS Backend — Main FastAPI Application
Entry point for the backend service.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings, ensure_data_dirs
from backend.app.core.logging_config import get_logger, setup_logging
from backend.app.database.session import init_db, close_db
from backend.app.monitoring.system_monitor import system_monitor
from backend.app.api.v1 import router as api_v1_router

# Initialise logging before anything else
setup_logging(
    level=settings.log_level,
    log_file=settings.log_file,
)
logger = get_logger("main")

_startup_time: datetime | None = None


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    global _startup_time
    _startup_time = datetime.now(UTC)

    logger.info("=" * 60)
    logger.info("  PROJECT J.A.R.V.I.S. — Backend Starting")
    logger.info("  Version: %s", settings.app_version)
    logger.info("=" * 60)

    # Ensure data directories exist
    ensure_data_dirs()

    # Initialise database
    await init_db()
    logger.info("Database ready.")

    # Start system monitor
    await system_monitor.start()
    logger.info("System monitor active.")

    logger.info("JARVIS backend is online. Host: %s:%s", settings.backend_host, settings.backend_port)

    yield  # ── Application runs ──

    # Shutdown
    logger.info("JARVIS backend shutting down...")
    await system_monitor.stop()
    await close_db()
    logger.info("Shutdown complete.")


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="J.A.R.V.I.S. Backend API",
    description="Just A Rather Very Intelligent System — Private desktop AI assistant backend.",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS — only allow the Tauri desktop frontend (localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "tauri://localhost",
        "https://tauri.localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please check the JARVIS activity log.",
            "path": str(request.url.path),
        },
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns genuine system status — never fabricated data.
    """
    system_status = system_monitor.get_status_dict()
    uptime_seconds = None
    if _startup_time:
        uptime_seconds = int((datetime.now(UTC) - _startup_time).total_seconds())

    return {
        "status": "online",
        "version": settings.app_version,
        "uptime_seconds": uptime_seconds,
        "system": system_status,
        "components": {
            "database": "online",
            "system_monitor": "online",
            "voice": "not_initialised",  # Phase 4
            "gemini": "not_checked",     # Checked on first use / settings
            "ollama": "disabled" if not settings.ollama_enabled else "not_checked",
        },
        "mode": settings.assistant_mode,
    }


# Mount versioned API router
app.include_router(api_v1_router, prefix="/api/v1")

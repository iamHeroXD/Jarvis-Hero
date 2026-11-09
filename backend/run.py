"""
JARVIS Backend — Entry point
Run with: python -m backend.run
Or: uvicorn backend.app.main:app --host 127.0.0.1 --port 8765
"""
import uvicorn
from backend.app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
        log_level=settings.log_level.lower(),
    )

#!/usr/bin/env python3
"""
Main entry point for SSI Holder FastAPI application
"""
import uvicorn
from app import create_app
from app.config import settings

# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
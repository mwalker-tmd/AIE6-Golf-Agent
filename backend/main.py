import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import router as api_router
from backend.core.logging_config import logger
from dotenv import load_dotenv
from starlette.requests import Request

load_dotenv()

app = FastAPI()

from starlette.requests import Request

@app.middleware("http")
async def log_request_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    logger.debug(f"Incoming request from Origin: {origin} | Path: {request.url.path}")
    response = await call_next(request)
    return response

# CORS middleware to allow frontend to talk to the backend
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    try:
        # Try to parse as JSON array (recommended: '["url1", "url2"]')
        ALLOWED_ORIGINS = json.loads(allowed_origins_env)
        if isinstance(ALLOWED_ORIGINS, str):
            ALLOWED_ORIGINS = [ALLOWED_ORIGINS]
    except json.JSONDecodeError:
        # Fallback: treat as comma-separated string
        ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Development
        "http://localhost:7860",  # Production
        "http://127.0.0.1:5173",  # Development alternative
        "http://127.0.0.1:7860",  # Production alternative
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

@app.middleware("http")
async def log_origin_and_path(request, call_next):
    origin = request.headers.get("origin")
    logger.debug(f"CORS DEBUG: Origin={origin}, Path={request.url.path}")
    response = await call_next(request)
    return response

# Include the API endpoints
app.include_router(api_router, prefix="/api")

# This directs FastAPI to serve the React build from '/' (root) -- NOTE: This is only required for production only
if os.getenv("ENVIRONMENT") == "production":
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# Log available routes on startup
logger.info("Available routes:")
for route in app.routes:
    logger.debug(f"🔗 ROUTE: {route.path} → {route.name}")

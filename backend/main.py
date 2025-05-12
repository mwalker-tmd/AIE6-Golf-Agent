import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import router as api_router
from .core.logging_config import logger
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware to allow frontend to talk to the backend

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the API endpoints
app.include_router(api_router, prefix="/api")

# This directs FastAPI to serve the React build from '/' (root) -- NOTE: This is only required for production only
if os.getenv("ENVIRONMENT") == "production":
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# Log available routes on startup
logger.info("Available routes:")
for route in app.routes:
    logger.debug(f"🔗 ROUTE: {route.path} → {route.name}")

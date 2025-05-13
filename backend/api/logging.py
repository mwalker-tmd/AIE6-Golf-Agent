from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from enum import Enum
from backend.core.logging_config import set_log_level, get_log_level, logger

router = APIRouter()

class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@router.get("/log-level")
async def get_current_log_level():
    """Get the current logging level."""
    return {"level": get_log_level()}

@router.post("/log-level")
async def update_log_level(level: LogLevelEnum = Query(..., description="Log level")):
    """Update the logging level."""
    try:
        set_log_level(level)
        return {"message": f"Log level set to {level}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
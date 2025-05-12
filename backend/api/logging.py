from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.logging_config import set_log_level, get_log_level, logger

router = APIRouter()

class LogLevel(BaseModel):
    level: str

@router.get("/log-level")
async def get_current_log_level():
    """Get the current logging level."""
    return {"level": get_log_level()}

@router.post("/log-level")
async def update_log_level(log_level: LogLevel):
    """Update the logging level."""
    try:
        set_log_level(log_level.level)
        return {"message": f"Log level set to {log_level.level}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
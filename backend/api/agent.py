from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.golf_langgraph import create_graph
from backend.core.logging_config import logger
import traceback

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def query_agent(request: QueryRequest):
    try:
        graph = create_graph()
        result = await graph.ainvoke({"input": request.query})
        return {"response": result["final_response"]}
    except Exception as e:
        logger.error("Exception in /query endpoint:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


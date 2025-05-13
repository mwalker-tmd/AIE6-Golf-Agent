from fastapi import APIRouter, HTTPException, Form
from backend.agents.golf_langgraph import create_graph
from backend.core.logging_config import logger
import traceback

router = APIRouter()

@router.post("/query")
async def query_agent(query: str = Form(...)):
    try:
        graph = create_graph()
        result = await graph.ainvoke({"input": query})
        return {"response": result["final_response"]}
    except Exception as e:
        logger.error("Exception in /query endpoint:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


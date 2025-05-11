from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.golf_langgraph import create_graph
from backend.tools.utils import debug_print
import traceback

router = APIRouter()

class Query(BaseModel):
    query: str

@router.post("/query")
async def query_agent(query: Query):
    try:
        graph = create_graph()
        result = await graph.ainvoke({"input": query.query})
        return {"response": result["final_response"]}
    except Exception as e:
        print("Exception in /query endpoint:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents.golf_langgraph import graph as agent

router = APIRouter()

class AgentRequest(BaseModel):
    query: str

@router.post(
    "/agent",
    tags=["Agent"],
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/AgentRequest"}
                }
            }
        }
    }
)
async def run_agent(request: AgentRequest):
    """
    Executes the agent with the given query input.

    Parameters
    ----------
    query : str
        A JSON object with a "query" key.

    Returns
    -------
    dict
        The final string response from the agent.
        Example:
        {
            "response": "You said: Hello world"
        }
    """
    query = request.query
    debug_print(f"🧪 query object: {query}")
    payload = {"input": query}

    debug_print(f"🧪 Invoking agent object {agent} with: {payload}")
    result = await agent.ainvoke(payload)
    
    #return {"response": output}
    return {"response": result["final_response"]}

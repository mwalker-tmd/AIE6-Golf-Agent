import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.agents import Tool
from typing import TypedDict, Optional
from backend.tools.registry import tools
from backend.tools.utils import debug_print

load_dotenv()
class AgentState(TypedDict, total=False):
    input: str
    tool_result: Optional[str]
    final_response: Optional[str]

# lazy instatiation of the llm:
def get_llm():
    return ChatOpenAI(
        temperature=0.3,
        model="gpt-4",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

# Router logic only (used in conditional_edges)
def get_tool_route(state: AgentState) -> str:
    debug_print(f"[ROUTER FUNC] Routing from state: {state}")
    query = state.get("input")
    if not query:
        raise ValueError(f"[ROUTER FUNC ERROR] Missing 'input' key in state: {state}")

    if "stat" in query.lower() or "compare" in query.lower():
        return "get_pro_stats"
    elif "course" in query.lower() or "yardage" in query.lower():
        return "course_insights"
    else:
        return "search_golfpedia"

# Router node that simply passes state through
def pass_through_router(state: AgentState) -> AgentState:
    debug_print(f"[ROUTER NODE] Received state: {state}")
    if "input" not in state:
        raise ValueError(f"[ROUTER NODE ERROR] Missing 'input' key in state: {state}")
    return state

# Tool execution logic
tool_map = {t.name: t for t in tools}

def wrap_tool(name):
    tool = tool_map[name]
    def run(state: AgentState):
        debug_print(f"[TOOL NODE] Running tool: {name} with input: {state.get('input')}")
        result = tool.invoke(state["input"])
        return AgentState({**state, "tool_result": result})
    return RunnableLambda(run)

# Summary node
def summarize_result(state: AgentState):
    debug_print(f"[SUMMARY NODE] Received tool result: {state.get('tool_result')}")
    summary = get_llm().invoke([
        HumanMessage(content=f'''You are a golf research assistant. Here is the tool result:

{state["tool_result"]}

Please summarize the answer as a helpful response to the user query: "{state["input"]}"''')
    ])
    return AgentState({**state, "final_response": summary.content})

# Build the graph
builder = StateGraph(AgentState)

builder.add_node("router", RunnableLambda(pass_through_router))
for tool_name in tool_map:
    builder.add_node(tool_name, wrap_tool(tool_name))
builder.add_node("summarize", RunnableLambda(summarize_result))

builder.set_entry_point("router")
builder.add_conditional_edges("router", get_tool_route)
for name in tool_map:
    builder.add_edge(name, "summarize")
builder.add_edge("summarize", END)

graph = builder.compile()

# Optional standalone test
if __name__ == "__main__":
    import asyncio

    from pprint import pprint

    print("🚀 Running standalone agent test...")
    result = asyncio.run(graph.ainvoke({"input": "Compare Scottie Scheffler and Rory McIlroy in putting"}))
    pprint(result)

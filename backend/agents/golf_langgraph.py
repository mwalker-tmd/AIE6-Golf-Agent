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

# lazy instantiation of the llm:
def get_llm():
    return ChatOpenAI(
        temperature=0.3,
        model="gpt-4",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

def route_with_llm(state: AgentState) -> str:
    query = state.get("input")
    if not query:
        raise ValueError("[ROUTER FUNC ERROR] No input found in state.")

    llm = get_llm()
    response = llm.invoke([
        HumanMessage(content=f"""Classify this golf-related query into one of the following categories:
- "get_pro_stats": if it compares or asks about player stats
- "course_insights": if it's asking about a specific golf course
- "get_shot_recommendations": if it's asking about club selection, shot technique, or avoiding certain shot patterns
- "search_golfpedia": for all other general golf knowledge

Respond with just one word: get_pro_stats, course_insights, get_shot_recommendations, or search_golfpedia.

Query: "{query}" """)
    ])

    tool_name = response.content.strip()
    debug_print(f"[ROUTER FUNC w/ LLM] Routed '{query}' → {tool_name}")
    print(f"[DEBUG] Router output: '{tool_name}'")
    # return tool_name
    return {"next": tool_name}  # ✅ FIXED: wrap the string in a dictionary

# Tool execution logic
tool_map = {t.name: t for t in tools}

def wrap_tool(name):
    tool = tool_map[name]
    def run(state: AgentState):
        debug_print(f"[TOOL NODE] Running tool: {name} with input: {state.get('input')}")
        result = tool.invoke(state["input"])
        print(f"[DEBUG] Tool '{name}' result type: {type(result)} value: {result}")
        print(f"[DEBUG] Tool.invoke for '{name}': {getattr(tool, 'invoke', None)}, type: {type(getattr(tool, 'invoke', None))}")
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
    # return AgentState({**state, "final_response": summary.content})
    return {"final_response": summary.content}  # ✅ Return plain dict

def create_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("router", route_with_llm)
    for tool_name in tool_map:
        print(f"[DEBUG] Adding node: {tool_name} with {wrap_tool(tool_name)}")
        workflow.add_node(tool_name, wrap_tool(tool_name))
    workflow.add_node("summarize", RunnableLambda(summarize_result))

    # Add edges
    workflow.add_conditional_edges("router", lambda state: state["next"])
    for tool_name in tool_map:
        workflow.add_edge(tool_name, "summarize")
    workflow.add_edge("summarize", END)

    # debug info:
    print(f"[DEBUG] All nodes in workflow: {list(workflow.nodes.keys())}")
    for name, node in workflow.nodes.items():
        print(f"[DEBUG] Node '{name}' is of type {type(node)} and value: {node}")
    
    # Set entry point
    workflow.set_entry_point("router")

    return workflow.compile()

# Create the graph instance
graph = create_graph()

# Optional standalone test
if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    print("🚀 Running standalone agent test...")
    result = asyncio.run(graph.ainvoke({"input": "How do I hit a flop shot?"}))
    pprint(result)

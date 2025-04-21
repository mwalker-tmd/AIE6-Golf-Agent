"""
Tool registry for the agent. Add tools here to make them available to your agent's toolbox.
"""

from langchain.tools import Tool
from backend.tools.search_golfpedia_tool import search_golfpedia

tools = [
    Tool(
        name="search_golfpedia",
        func=search_golfpedia,
        description="Searches the web for general golf-related knowledge using Tavily.",
    ),
    # Add other tools here later
]

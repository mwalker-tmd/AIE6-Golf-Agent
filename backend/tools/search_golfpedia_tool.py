import os
from tavily import TavilyClient
from langchain.tools import tool
from backend.tools.constants_tools import NO_SUMMARY_AVAILABLE

# Initialize the client lazily to allow for environment variable mocking in tests
def get_tavily_client():
    return TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

@tool
def search_golfpedia(query: str) -> str:
    """Searches the web for general golf-related knowledge using Tavily."""
    tavily = get_tavily_client()
    result = tavily.search(query=query, search_depth="basic")
    return result["answer"] if "answer" in result else NO_SUMMARY_AVAILABLE

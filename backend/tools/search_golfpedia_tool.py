import os
import json
from tavily import TavilyClient
from langchain.tools import tool
from backend.tools.constants_tools import NO_SUMMARY_AVAILABLE
from backend.core.logging_config import logger

# Initialize the client lazily to allow for environment variable mocking in tests
def get_tavily_client():
    return TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

@tool
def search_golfpedia(query: str) -> str:
    """Searches the web for general golf-related knowledge. Examples include: information about golf terms, rules, and concepts."""
    logger.debug(f"[TOOL CALLED] search_golfpedia: {query}")
    
    try:
        result = search_golfpedia_api(query)
        logger.debug(f"[TOOL RESULT] search_golfpedia: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        return f"Error searching Golfpedia: {str(e)}"

def search_golfpedia_api(query: str) -> str:
    tavily = get_tavily_client()
    result = tavily.search(query=query, search_depth="basic")
    
    # If there's a direct answer, return it
    if result.get("answer"):
        return result["answer"]
    
    # If there are search results, format them into a readable string
    if result.get("results") and len(result["results"]) > 0:
        formatted_results = "Here are some relevant search results:\n\n"
        for i, item in enumerate(result["results"][:5], 1):  # Limit to top 5 results
            formatted_results += f"{i}. {item.get('title', 'No title')}\n"
            formatted_results += f"   {item.get('content', 'No content')}\n"
            formatted_results += f"   Source: {item.get('url', 'No URL')}\n\n"
        return formatted_results
    
    # If no answer and no results, return the default message
    return NO_SUMMARY_AVAILABLE

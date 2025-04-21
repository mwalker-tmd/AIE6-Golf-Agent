"""
Tool registry for the agent. Add tools here to make them available to your agent's toolbox.
"""

from langchain.tools import Tool
from backend.tools.search_golfpedia_tool import search_golfpedia
from backend.tools.course_insights_tool import course_insights
tools = [
    Tool(
        name="search_golfpedia",
        func=search_golfpedia,
        description="Searches the web for general golf-related knowledge using Tavily.",
    ),
    Tool(
        name="course_insights",
        func=course_insights,
        description="Fetches detailed course info for a given golf course name using GolfCourseAPI.",
    ),
    # Add other tools here later
]

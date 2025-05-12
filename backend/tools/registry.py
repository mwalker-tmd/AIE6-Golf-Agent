"""
Tool registry for the agent. Add tools here to make them available to your agent's toolbox.
"""

from langchain.tools import Tool
from backend.tools.search_golfpedia_tool import search_golfpedia
from backend.tools.course_insights_tool import course_insights
from backend.tools.get_pro_stats_tool import get_pro_stats
from backend.tools.golf_shot_recommendations_tool import get_shot_recommendations

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
    Tool(
        name="get_pro_stats",
        func=get_pro_stats,
        description="Returns mock player stat comparisons from a simulated PGA database.",
    ),
    Tool(
        name="get_shot_recommendations",
        func=get_shot_recommendations,
        description="Retrieves relevant golf shot recommendations based on the query using semantic search. Useful for questions about club selection, shot technique, or avoiding certain shot patterns.",
    ),
    # Add other tools here later
]

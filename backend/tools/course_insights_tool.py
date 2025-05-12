import os
import json
import requests
from langchain.tools import tool
from backend.core.logging_config import logger

BASE_URL = "https://api.golfcourseapi.com/v1"

def get_headers():
    """Get the headers with the API key."""
    api_key = os.environ.get("GOLFCOURSE_API_KEY", "fake-api-key")
    return {
        "Authorization": f"Key {api_key}"
    }

@tool
def course_insights(search_query: str) -> str:
    """
    Get information about golf courses, including course details, tee options, and ratings.
    
    Args:
        search_query: A query string to search for golf courses
        
    Returns:
        A JSON string containing course information
    """
    
    logger.debug(f"[TOOL CALLED] course_insights: {search_query}")

    if not search_query.strip():
        return f"No courses found for query '{search_query}'."

    try:
        # Step 1: Search
        search_resp = requests.get(f"{BASE_URL}/search", headers=get_headers(), params={"search_query": search_query})
        search_resp.raise_for_status()
        try:
            courses = search_resp.json().get("courses", [])
            logger.debug(f"[TOOL RESULT] course_insights: {json.dumps(search_resp.json())}")
            logger.debug(f"Number of courses found: {len(courses)}")
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] JSONDecodeError: {e}")
            return "An unexpected error occurred: Invalid JSON"

        if not courses:
            return f"No courses found for query '{search_query}'."
        else:
            logger.debug(f"Number of courses found: {len(courses)}")

        for course_meta in courses:
            course_id = course_meta["id"]
            course_name = course_meta["course_name"]
            club_name = course_meta["club_name"]

            detail_resp = requests.get(f"{BASE_URL}/courses/{course_id}", headers=get_headers())
            detail_resp.raise_for_status()
            try:
                data = detail_resp.json()
                course = data.get("course", {})
            except json.JSONDecodeError as e:
                logger.error(f"[ERROR] JSONDecodeError: {e}")
                return "An unexpected error occurred: Invalid JSON"

            tees = course.get("tees", {})
            all_tees = []

            if "male" in tees and tees["male"]:
                all_tees.extend(tees["male"])
            if "female" in tees and tees["female"]:
                all_tees.extend(tees["female"])

            logger.debug(f"Number of tees found: {len(all_tees)}")
            
            if all_tees:
                tee = all_tees[0]  # Use the first tee available
                return (
                    f"{club_name} - {course_name} (ID: {course_id})\n"
                    f"Location: {course.get('location', {}).get('address', 'Address not available')}\n"
                    f"Rating: {tee.get('course_rating', 'N/A')} | Slope: {tee.get('slope_rating', 'N/A')}\n"
                    f"Yards: {tee.get('total_yards', 'N/A')} | Par: {tee.get('par_total', 'N/A')}\n"
                    f"Hardest Hole: TBD\n"
                )

        # fallback if none have tee data
        return f"No tee data available for any course found for query '{search_query}'."

    except requests.HTTPError as e:
        logger.error(f"[ERROR] HTTPError: {e}")
        return f"API request failed: {e}"
    except Exception as e:
        logger.error(f"[ERROR] Unexpected exception: {e}")
        return f"An unexpected error occurred: {str(e)}"

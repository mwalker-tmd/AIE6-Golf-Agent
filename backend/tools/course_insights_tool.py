import os
import requests
from langchain.tools import tool

GOLFCOURSE_API_KEY = os.environ["GOLFCOURSE_API_KEY"]
BASE_URL = "https://api.golfcourseapi.com/v1"

HEADERS = {
    "Authorization": f"Key {GOLFCOURSE_API_KEY}"
}

@tool
def course_insights(search_query: str) -> str:
    """Fetches detailed course info for a given golf course name using GolfCourseAPI."""
    try:
        # Step 1: Search
        search_resp = requests.get(f"{BASE_URL}/search", headers=HEADERS, params={"search_query": search_query})
        search_resp.raise_for_status()
        courses = search_resp.json().get("courses", [])

        if not courses:
            return f"No courses found for query '{search_query}'."

        course_id = courses[0]["id"]
        course_name = courses[0]["course_name"]
        club_name = courses[0]["club_name"]

        # Step 2: Fetch course by ID
        detail_resp = requests.get(f"{BASE_URL}/courses/{course_id}", headers=HEADERS)
        detail_resp.raise_for_status()
        course = detail_resp.json()

        male_tees = course.get("tees", {}).get("male", [])
        if not male_tees:
            return f"No male tee data available for {club_name} - {course_name}."

        tee = male_tees[0]  # Assume the first tee (often the back tees)

        return (
            f"{club_name} - {course_name} (ID: {course_id})\n"
            f"Location: {course['location']['address']}\n"
            f"Rating: {tee['course_rating']} | Slope: {tee['slope_rating']}\n"
            f"Yards: {tee['total_yards']} | Par: {tee['par_total']}\n"
            f"Hardest Hole: TBD\n"
        )

    except requests.HTTPError as e:
        return f"API request failed: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

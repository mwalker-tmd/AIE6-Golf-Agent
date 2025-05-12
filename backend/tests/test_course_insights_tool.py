import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from backend.tools.course_insights_tool import course_insights

@pytest.fixture(autouse=True)
def fake_env():
    """Mock environment variables for all tests."""
    with patch.dict(os.environ, {"GOLFCOURSE_API_KEY": "fake-api-key"}):
        yield

@pytest.fixture
def mock_search_response():
    return {
        "courses": [
            {
                "id": "12345",
                "course_name": "Championship Course",
                "club_name": "Pine Valley Golf Club"
            }
        ]
    }

@pytest.fixture
def mock_detail_response():
    return {
        "course": {
            "location": {
                "address": "123 Golf Lane, Pine Valley, NJ 08021"
            },
            "tees": {
                "male": [
                    {
                        "course_rating": 74.1,
                        "slope_rating": 155,
                        "total_yards": 7280,
                        "par_total": 72
                    }
                ]
            }
        }
    }

@pytest.fixture
def mock_requests_get():
    """Mock the requests.get method."""
    with patch('requests.get') as mock:
        yield mock

# @pytest.fixture
# def mock_requests():
#     """Mock the requests module to avoid actual API calls."""
#     with patch('backend.tools.course_insights_tool.requests') as mock:
#         # Set up the get method to return a mock response
#         mock_response = MagicMock()
#         mock_response.json.return_value = {}
#         mock_response.raise_for_status.return_value = None
#         mock.get.return_value = mock_response
#         yield mock

def test_course_insights_successful(mock_search_response, mock_detail_response, mock_requests_get):
    """Test successful course insights retrieval"""
    # Set up the mock responses
    search_response = MagicMock()
    search_response.json.return_value = mock_search_response
    search_response.raise_for_status.return_value = None
    
    detail_response = MagicMock()
    detail_response.json.return_value = mock_detail_response
    detail_response.raise_for_status.return_value = None
    
    # Configure the mock to return different responses for different URLs
    mock_requests_get.side_effect = [search_response, detail_response]
    
    # Call the function
    result = course_insights.invoke("Pine Valley Course")
    
    # Verify the result
    expected_result = (
        "Pine Valley Golf Club - Championship Course (ID: 12345)\n"
        "Location: 123 Golf Lane, Pine Valley, NJ 08021\n"
        "Rating: 74.1 | Slope: 155\n"
        "Yards: 7280 | Par: 72\n"
        "Hardest Hole: TBD\n"
    )
    assert result == expected_result
    
    # Verify the API calls
    mock_requests_get.assert_any_call(
        "https://api.golfcourseapi.com/v1/search", 
        headers={"Authorization": "Key fake-api-key"}, 
        params={"search_query": "Pine Valley Course"}
    )
    mock_requests_get.assert_any_call(
        "https://api.golfcourseapi.com/v1/courses/12345", 
        headers={"Authorization": "Key fake-api-key"}
    )

def test_course_insights_no_courses_found(mock_requests_get):
    """Test when no courses are found for the search query"""
    # Set up the mock response
    search_response = MagicMock()
    search_response.json.return_value = {"courses": []}
    search_response.raise_for_status.return_value = None
    
    # Configure the mock
    mock_requests_get.return_value = search_response
    
    # Call the function
    result = course_insights.invoke("Nonexistent Golf Club")
    
    # Verify the result
    assert result == "No courses found for query 'Nonexistent Golf Club'."

def test_course_insights_no_tee_data(mock_search_response, mock_requests_get):
    """Test when no tee data is available for the course"""
    # Set up the mock responses
    search_response = MagicMock()
    search_response.json.return_value = mock_search_response
    search_response.raise_for_status.return_value = None
    
    detail_response = MagicMock()
    detail_response.json.return_value = {
        "course": {
            "location": {"address": "123 Golf Lane"},
            "tees": {"male": [], "female": []}
        }
    }
    detail_response.raise_for_status.return_value = None
    
    # Configure the mock
    mock_requests_get.side_effect = [search_response, detail_response]
    
    # Call the function
    result = course_insights.invoke("Pine Valley")
    
    # Verify the result
    assert result == "No tee data available for any course found for query 'Pine Valley'."

def test_course_insights_female_tee_data(mock_search_response, mock_requests_get):
    """Test when only female tee data is available"""
    # Set up the mock responses
    search_response = MagicMock()
    search_response.json.return_value = mock_search_response
    search_response.raise_for_status.return_value = None
    
    detail_response = MagicMock()
    detail_response.json.return_value = {
        "course": {
            "location": {"address": "123 Golf Lane, Pine Valley, NJ 08021"},
            "tees": {
                "male": [],
                "female": [
                    {
                        "course_rating": 72.5,
                        "slope_rating": 140,
                        "total_yards": 6500,
                        "par_total": 72
                    }
                ]
            }
        }
    }
    detail_response.raise_for_status.return_value = None
    
    # Configure the mock
    mock_requests_get.side_effect = [search_response, detail_response]
    
    # Call the function
    result = course_insights.invoke("Pine Valley")
    
    # Verify the result
    expected_result = (
        "Pine Valley Golf Club - Championship Course (ID: 12345)\n"
        "Location: 123 Golf Lane, Pine Valley, NJ 08021\n"
        "Rating: 72.5 | Slope: 140\n"
        "Yards: 6500 | Par: 72\n"
        "Hardest Hole: TBD\n"
    )
    assert result == expected_result

def test_course_insights_http_error(mock_requests_get):
    """Test handling of HTTP error"""
    # Set up the mock to raise an exception with a 404 error message
    mock_requests_get.side_effect = requests.HTTPError("404 Not Found")
    
    # Call the function
    result = course_insights.invoke("Pine Valley")
    
    # Verify the result
    assert result.startswith("API request failed")

def test_course_insights_unexpected_error(mock_requests_get):
    """Test handling of unexpected exception"""
    # Set up the mock to raise an unexpected exception
    mock_requests_get.side_effect = ValueError("Invalid JSON")

    # Call the function
    result = course_insights.invoke("Pine Valley")

    # Verify the result
    assert "An unexpected error occurred" in result
    assert "Invalid JSON" in result

@pytest.mark.parametrize("query", ["", "   ", "\n", "\t"])
def test_course_insights_empty_query(query, mock_requests_get):
    """Test handling of empty or whitespace-only queries"""
    # Set up the mock response
    search_response = MagicMock()
    search_response.json.return_value = {"courses": []}
    search_response.raise_for_status.return_value = None
    
    # Configure the mock
    mock_requests_get.return_value = search_response
    
    # Call the function
    result = course_insights.invoke(query)
    
    # Verify the result
    assert result == f"No courses found for query '{query}'."

def test_course_insights_missing_location(mock_search_response, mock_requests_get):
    """Test when location data is missing"""
    search_response = MagicMock()
    search_response.json.return_value = mock_search_response
    search_response.raise_for_status.return_value = None

    detail_response = MagicMock()
    detail_response.json.return_value = {
        "course": {
            "tees": {"male": [{"course_rating": 74.1, "slope_rating": 155, "total_yards": 7280, "par_total": 72}]}
            # Missing "location"
        }
    }
    detail_response.raise_for_status.return_value = None

    mock_requests_get.side_effect = [search_response, detail_response]
    result = course_insights.invoke("Pine Valley")
    
    # Verify the result
    expected_result = (
        "Pine Valley Golf Club - Championship Course (ID: 12345)\n"
        "Location: Address not available\n"
        "Rating: 74.1 | Slope: 155\n"
        "Yards: 7280 | Par: 72\n"
        "Hardest Hole: TBD\n"
    )
    assert result == expected_result

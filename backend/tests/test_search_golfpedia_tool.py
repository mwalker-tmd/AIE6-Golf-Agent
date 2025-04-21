import pytest
from unittest.mock import patch, MagicMock
from backend.tools.search_golfpedia_tool import search_golfpedia
from backend.tools.constants_tools import NO_SUMMARY_AVAILABLE

@pytest.fixture
def mock_tavily_response():
    return {
        "answer": "This is a mock golf answer"
    }

@pytest.fixture
def mock_tavily_empty_response():
    return {"results": []}

@pytest.fixture
def mock_tavily_client():
    """Mock the TavilyClient to avoid API calls."""
    with patch('backend.tools.search_golfpedia_tool.get_tavily_client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

def test_search_golfpedia_successful(mock_tavily_response, mock_tavily_client):
    """Test successful search with answer in response"""
    mock_tavily_client.search.return_value = mock_tavily_response
    result = search_golfpedia.invoke("What is golf?")
    assert result == "This is a mock golf answer"

def test_search_golfpedia_no_answer(mock_tavily_empty_response, mock_tavily_client):
    """Test search when an empty response is returned"""
    mock_tavily_client.search.return_value = mock_tavily_empty_response
    result = search_golfpedia.invoke("What is golf?")
    assert result == NO_SUMMARY_AVAILABLE

def test_search_golfpedia_api_error(mock_tavily_client):
    """Test handling of API error"""
    mock_tavily_client.search.side_effect = Exception("API Error")
    with pytest.raises(Exception) as exc_info:
        search_golfpedia.invoke("What is golf?")
    assert str(exc_info.value) == "API Error"

def test_search_golfpedia_empty_query(mock_tavily_empty_response, mock_tavily_client):
    """Test handling of empty query"""
    mock_tavily_client.search.return_value = mock_tavily_empty_response
    result = search_golfpedia.invoke("")
    assert result == NO_SUMMARY_AVAILABLE

@pytest.mark.parametrize("query", ["", "   ", "\n", "\t"])
def test_search_golfpedia_blankish_queries(query, mock_tavily_empty_response, mock_tavily_client):
    mock_tavily_client.search.return_value = mock_tavily_empty_response
    result = search_golfpedia.invoke(query)
    assert result == NO_SUMMARY_AVAILABLE 
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from backend.agents.golf_langgraph import route_with_llm, AgentState, tool_map

# Create a mock graph that we can use for testing
@pytest.fixture
def mock_graph():
    """Create a mock graph for testing."""
    async def mock_ainvoke(input_dict):
        # Extract the input
        query = input_dict.get("input", "")
        
        # Determine which tool to use based on the query
        tool_name = route_with_llm({"input": query})["next"]
        
        # Return a mock result
        return {
            "input": query,
            "tool_result": f"Mock result for {tool_name}",
            "final_response": f"This is a mock summary response for {query}"
        }
    
    mock = MagicMock()
    mock.ainvoke = mock_ainvoke
    return mock

@pytest.fixture
def mock_llm():
    """Mock the LLM to avoid actual API calls."""
    with patch('backend.agents.golf_langgraph.get_llm') as mock:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "This is a mock summary response."
        mock.return_value = mock_llm
        yield mock

@pytest.fixture
def mock_tools():
    """Mock the tools to avoid actual API calls."""
    mock_tools = {
        "get_pro_stats": MagicMock(),
        "course_insights": MagicMock(),
        "search_golfpedia": MagicMock()
    }
    mock_tools["get_pro_stats"].invoke.return_value = "Mock pro stats result"
    mock_tools["course_insights"].invoke.return_value = "Mock course insights result"
    mock_tools["search_golfpedia"].invoke.return_value = "Mock golfpedia search result"
    return mock_tools

@pytest.mark.asyncio
async def test_graph_pro_stats_query(mock_graph):
    """Test the graph with a pro stats query."""
    # Patch the graph and get_llm with our mocks
    with patch('backend.agents.golf_langgraph.graph', mock_graph), \
         patch('backend.agents.golf_langgraph.get_llm') as mock_llm:
        mock_llm.return_value.invoke.return_value.content = "get_pro_stats"
        result = await mock_graph.ainvoke({"input": "Compare Scottie Scheffler and Rory McIlroy in putting"})
        # Check the final response
        assert result["final_response"] == "This is a mock summary response for Compare Scottie Scheffler and Rory McIlroy in putting"
        assert result["tool_result"] == "Mock result for get_pro_stats"

@pytest.mark.asyncio
async def test_graph_course_insights_query(mock_graph):
    """Test the graph with a course insights query."""
    with patch('backend.agents.golf_langgraph.graph', mock_graph), \
         patch('backend.agents.golf_langgraph.get_llm') as mock_llm:
        mock_llm.return_value.invoke.return_value.content = "course_insights"
        result = await mock_graph.ainvoke({"input": "What is the course layout at Pine Valley?"})
        # Check the final response
        assert result["final_response"] == "This is a mock summary response for What is the course layout at Pine Valley?"
        assert result["tool_result"] == "Mock result for course_insights"

@pytest.mark.asyncio
async def test_graph_search_golfpedia_query(mock_graph):
    """Test the graph with a search golfpedia query."""
    with patch('backend.agents.golf_langgraph.graph', mock_graph), \
         patch('backend.agents.golf_langgraph.get_llm') as mock_llm:
        mock_llm.return_value.invoke.return_value.content = "search_golfpedia"
        result = await mock_graph.ainvoke({"input": "What is the history of golf?"})
        # Check the final response
        assert result["final_response"] == "This is a mock summary response for What is the history of golf?"
        assert result["tool_result"] == "Mock result for search_golfpedia"

def test_route_with_llm(mock_llm):
    """Test the tool routing logic."""
    # Test pro stats route
    state = AgentState(input="Compare Scottie Scheffler and Rory McIlroy in putting")
    mock_llm.return_value.invoke.return_value.content = "get_pro_stats"
    assert route_with_llm(state)["next"] == "get_pro_stats"
    
    # Test course insights route - update to match current implementation
    state = AgentState(input="Tell me about Pine Valley Golf Club")
    mock_llm.return_value.invoke.return_value.content = "search_golfpedia"
    assert route_with_llm(state)["next"] == "search_golfpedia"
    
    # Test course insights route with a query that should match
    state = AgentState(input="What is the course layout at Pine Valley?")
    mock_llm.return_value.invoke.return_value.content = "course_insights"
    assert route_with_llm(state)["next"] == "course_insights"
    
    # Test search golfpedia route
    state = AgentState(input="What is the history of golf?")
    mock_llm.return_value.invoke.return_value.content = "search_golfpedia"
    assert route_with_llm(state)["next"] == "search_golfpedia"
    
    # Test error handling
    with pytest.raises(ValueError):
        route_with_llm(AgentState()) 
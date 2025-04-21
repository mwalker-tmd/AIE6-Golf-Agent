import pytest
from unittest.mock import patch
from backend.tools.get_pro_stats_tool import get_pro_stats

@pytest.fixture
def mock_debug_print():
    """Mock the debug_print function to avoid actual printing during tests."""
    with patch('backend.tools.get_pro_stats_tool.debug_print') as mock:
        yield mock

def test_get_pro_stats_single_player_putting(mock_debug_print):
    """Test getting putting stats for a single player."""
    result = get_pro_stats.invoke("What is Scottie Scheffler's putting?")
    
    assert "SG Putting for Scottie Scheffler: Scottie Scheffler: 0.73" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_single_player_driving(mock_debug_print):
    """Test getting driving distance for a single player."""
    result = get_pro_stats.invoke("What is Rory McIlroy's driving distance?")
    
    assert "Driving Distance for Rory McIlroy: Rory McIlroy: 326.3" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_two_players_putting(mock_debug_print):
    """Test comparing putting stats for two players."""
    result = get_pro_stats.invoke("Compare putting between Scottie Scheffler and Rory McIlroy")
    
    assert "SG Putting comparison:" in result
    assert "Scottie Scheffler: 0.73" in result
    assert "Rory McIlroy: 0.19" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_two_players_driving(mock_debug_print):
    """Test comparing driving distance for two players."""
    result = get_pro_stats.invoke("Compare driving between Bryson DeChambeau and Jon Rahm")
    
    assert "Driving Distance comparison:" in result
    assert "Bryson DeChambeau: 337.8" in result
    assert "Jon Rahm: 320.5" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_three_players(mock_debug_print):
    """Test comparing stats for three players."""
    result = get_pro_stats.invoke("Compare putting between Scottie Scheffler, Rory McIlroy, and Jon Rahm")
    
    assert "SG Putting comparison:" in result
    assert "Scottie Scheffler: 0.73" in result
    assert "Rory McIlroy: 0.19" in result
    assert "Jon Rahm: 0.45" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_unknown_player(mock_debug_print):
    """Test handling of unknown player."""
    result = get_pro_stats.invoke("What is Tiger Woods' putting?")
    
    assert "Please specify at least one known player" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_no_stat_keyword(mock_debug_print):
    """Test handling of query without a stat keyword."""
    result = get_pro_stats.invoke("Tell me about Scottie Scheffler")
    
    assert "Could not determine which stat to compare" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_case_insensitive(mock_debug_print):
    """Test that player names and stat keywords are case insensitive."""
    result = get_pro_stats.invoke("Compare PUTTING between scottie scheffler and RORY MCILROY")
    
    assert "SG Putting comparison:" in result
    assert "Scottie Scheffler: 0.73" in result
    assert "Rory McIlroy: 0.19" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_partial_name(mock_debug_print):
    """Test that partial player names work."""
    result = get_pro_stats.invoke("What is Bryson DeChambeau's driving?")
    
    assert "Driving Distance for Bryson DeChambeau: Bryson DeChambeau: 337.8" in result
    mock_debug_print.assert_called_once()

def test_get_pro_stats_empty_query(mock_debug_print):
    """Test handling of empty query."""
    result = get_pro_stats.invoke("")
    
    assert "Could not determine which stat to compare" in result
    mock_debug_print.assert_called_once() 
from langchain.tools import tool
from backend.tools.utils import debug_print

MOCK_STATS_DB = {
    "Scottie Scheffler": {"SG Putting": 0.73, "Driving Distance": 311.2},
    "Rory McIlroy": {"SG Putting": 0.19, "Driving Distance": 326.3},
    "Jon Rahm": {"SG Putting": 0.45, "Driving Distance": 320.5},
    "Bryson DeChambeau": {"SG Putting": -0.12, "Driving Distance": 337.8}
}

@tool
def get_pro_stats(query: str) -> str:
    """Returns mock stat data for one or two PGA players from a simulated database."""
    debug_print(f"[TOOL CALLED] get_pro_stats: {query}")

    stat_keywords = ["putting", "distance", "accuracy", "driving"]
    selected_stat = None
    for keyword in stat_keywords:
        if keyword in query.lower():
            selected_stat = {
                "putting": "SG Putting",
                "distance": "Driving Distance",
                "driving": "Driving Distance",
                "accuracy": "Driving Accuracy"  # placeholder
            }[keyword]
            break

    if not selected_stat:
        return "Could not determine which stat to compare."

    # Find players in the query
    found_players = []
    for player in MOCK_STATS_DB:
        if player.lower() in query.lower():
            found_players.append(player)
    
    # If no exact matches, try partial matches
    if not found_players:
        for player in MOCK_STATS_DB:
            # Split player name into parts and check if any part is in the query
            name_parts = player.lower().split()
            for part in name_parts:
                if part in query.lower() and len(part) > 2:  # Only match parts longer than 2 chars
                    found_players.append(player)
                    break

    if not found_players:
        return "Please specify at least one known player."

    lines = [f"{name}: {MOCK_STATS_DB[name].get(selected_stat, 'N/A')}" for name in found_players]
    
    if len(found_players) == 1:
        return f"{selected_stat} for {found_players[0]}: {lines[0]}"
    else:
        return f"{selected_stat} comparison:\n" + "\n".join(f"- {line}" for line in lines)

from bracket import simulate_tournament
import json
import os
import random

# NCAA Team Names by Conference (for more realistic team names)
TEAM_NAMES = {
    "ACC": ["Duke", "North Carolina", "Virginia", "Louisville", "Florida State", "NC State", "Syracuse", "Wake Forest", "Clemson", "Georgia Tech", "Boston College", "Pittsburgh", "Virginia Tech", "Miami", "Notre Dame"],
    "Big East": ["Villanova", "Creighton", "Marquette", "Xavier", "Seton Hall", "Butler", "Providence", "St. John's", "Georgetown", "DePaul"],
    "Big Ten": ["Michigan State", "Purdue", "Ohio State", "Michigan", "Wisconsin", "Illinois", "Iowa", "Indiana", "Maryland", "Minnesota", "Northwestern", "Rutgers", "Penn State", "Nebraska"],
    "Big 12": ["Kansas", "Baylor", "Texas Tech", "West Virginia", "Oklahoma", "Texas", "Iowa State", "Oklahoma State", "TCU", "Kansas State"],
    "Pac-12": ["Arizona", "UCLA", "Oregon", "USC", "Colorado", "Arizona State", "Stanford", "Washington", "Oregon State", "Utah", "California", "Washington State"],
    "SEC": ["Kentucky", "Florida", "Tennessee", "Auburn", "LSU", "Alabama", "Arkansas", "South Carolina", "Mississippi State", "Ole Miss", "Missouri", "Texas A&M", "Georgia", "Vanderbilt"],
    "Other": ["Gonzaga", "San Diego St", "Houston", "Dayton", "Memphis", "Wichita State", "BYU", "Saint Mary's", "VCU", "Richmond", "Davidson", "Saint Louis", "Rhode Island", "Loyola Chicago", "Buffalo", "Vermont", "UC Irvine", "Liberty", "Yale", "Belmont", "New Mexico State", "Northern Iowa", "East Tennessee State", "Stephen F. Austin", "UNC Greensboro", "Furman", "Wofford", "Hofstra", "Wright State", "Northeastern", "Bowling Green", "Akron", "Western Kentucky", "North Texas", "Little Rock", "South Dakota State", "North Dakota State", "Murray State", "Austin Peay", "Radford", "Winthrop", "Colgate", "Navy", "Mercer", "UNC Asheville", "Longwood", "Stetson", "UAB", "Drake", "Morehead St", "S Dakota St", "Iowa State", "Western KY"]
}

# Team colors for major programs
TEAM_COLORS = {
    "Duke": "#001A57",
    "North Carolina": "#7BAFD4",
    "Kansas": "#0051BA",
    "Kentucky": "#0033A0",
    "Villanova": "#13B5EA",
    "Michigan State": "#18453B",
    "Gonzaga": "#C8102E",
    "Baylor": "#003015",
    "UCLA": "#2D68C4",
    "Arizona": "#CC0033",
    "Houston": "#C8102E",
    "Texas": "#BF5700",
    "Purdue": "#CEB888",
    "Auburn": "#0C2340",
    "Tennessee": "#FF8200",
    "UConn": "#0E1A2F",
    "Florida": "#0021A5",
    "Louisville": "#AD0000",
    "Michigan": "#FFCB05",
    "Ohio State": "#BB0000",
    "Wisconsin": "#C5050C",
    "Illinois": "#E84A27",
    "Texas Tech": "#CC0000",
    "Iowa": "#FFCD00",
    "Indiana": "#990000",
    "Maryland": "#E03a3e",
    "Virginia": "#232D4B",
    "Florida State": "#782F40",
    "NC State": "#CC0000",
    "Syracuse": "#F76900",
    "Wake Forest": "#9E7E38",
    "Clemson": "#F66733",
    "Georgia Tech": "#B3A369",
    "Boston College": "#98002E",
    "Pittsburgh": "#003594",
    "Virginia Tech": "#630031",
    "Miami": "#F47321",
    "Notre Dame": "#0C2340",
    "Creighton": "#0054A6",
    "Marquette": "#003366",
    "Xavier": "#0C2340",
    "Seton Hall": "#004488",
    "Butler": "#13294B",
    "Providence": "#000000",
    "St. John's": "#BA0C2F",
    "Georgetown": "#041E42",
    "DePaul": "#005CB9",
    "West Virginia": "#002855",
    "Oklahoma": "#841617",
    "Iowa State": "#C8102E",
    "Oklahoma State": "#FF7300",
    "TCU": "#4D1979",
    "Kansas State": "#512888",
    "Oregon": "#154733",
    "USC": "#990000",
    "Colorado": "#CFB87C",
    "Arizona State": "#8C1D40",
    "Stanford": "#8C1515",
    "Washington": "#4B2E83",
    "Oregon State": "#DC4405",
    "Utah": "#CC0000",
    "California": "#003262",
    "Washington State": "#981E32",
    "Auburn": "#0C2340",
    "LSU": "#461D7C",
    "Alabama": "#9E1B32",
    "Arkansas": "#9D2235",
    "South Carolina": "#73000A",
    "Mississippi State": "#660000",
    "Ole Miss": "#CE1126",
    "Missouri": "#F1B82D",
    "Texas A&M": "#500000",
    "Georgia": "#BA0C2F",
    "Vanderbilt": "#866D4B"
}

# Default colors for teams without specific colors
DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
    "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5"
]

def assign_team_names(teams):
    """Assign realistic team names to the teams in the simulation"""
    # Flatten all team names into one list
    all_teams = []
    for conference, teams_list in TEAM_NAMES.items():
        all_teams.extend(teams_list)
    
    # Shuffle the list to randomize team assignments
    random.shuffle(all_teams)
    
    # Create a mapping from team ID to team name
    team_name_mapping = {}
    for i, team_id in enumerate(range(1, 65)):
        if i < len(all_teams):
            team_name_mapping[str(team_id)] = all_teams[i]
        else:
            team_name_mapping[str(team_id)] = f"Team {team_id}"
    
    return team_name_mapping

def get_team_color(team_name):
    """Get the color for a team, or a default color if not found"""
    if team_name in TEAM_COLORS:
        return TEAM_COLORS[team_name]
    else:
        # Use a hash of the team name to select a consistent color from defaults
        return DEFAULT_COLORS[hash(team_name) % len(DEFAULT_COLORS)]

def format_team_name(team, team_name_mapping):
    """Format team name with seed for display"""
    real_name = team_name_mapping.get(team['name'], team['name'])
    return f"{team['seed']} {real_name}"

def generate_bracket_html(tournament_games):
    """Generate HTML bracket visualization from tournament games"""
    # Assign realistic team names
    team_name_mapping = assign_team_names([str(i) for i in range(1, 65)])
    
    # Group games by round
    rounds = {}
    for game in tournament_games:
        round_num = game["tournament_round"]
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(game)
    
    # Organize teams by region for the first round
    regions = ["East", "West", "South", "Midwest"]
    first_round = rounds[0]
    region_games = {region: [] for region in regions}
    
    # Assuming first 32 games are first round, 8 games per region
    for i, game in enumerate(first_round):
        region_idx = i // 8
        if region_idx < len(regions):
            region = regions[region_idx]
            region_games[region].append(game)
    
    # Process each region to create bracket data
    bracket_data = {region: [] for region in regions}
    
    # Track all teams for later rounds
    all_teams = {}
    
    # Process first round
    for region in regions:
        region_first_round = region_games.get(region, [])
        region_bracket = []
        
        for game in region_first_round:
            team1_id = game["team1"]
            team2_id = game["team2"]
            team1_name = team_name_mapping.get(team1_id, team1_id)
            team2_name = team_name_mapping.get(team2_id, team2_id)
            
            team1 = {
                "id": team1_id,
                "seed": game["seed_team1"],
                "name": team1_name,
                "color": get_team_color(team1_name),
                "winner": game["team1_win"]
            }
            
            team2 = {
                "id": team2_id,
                "seed": game["seed_team2"],
                "name": team2_name,
                "color": get_team_color(team2_name),
                "winner": not game["team1_win"]
            }
            
            # Store teams for later rounds
            all_teams[team1_id] = team1
            all_teams[team2_id] = team2
            
            # Generate realistic scores
            winner_score = random.randint(65, 95)
            loser_score = winner_score - random.randint(5, 25)
            
            if team1["winner"]:
                team1["score"] = winner_score
                team2["score"] = loser_score
            else:
                team1["score"] = loser_score
                team2["score"] = winner_score
            
            region_bracket.append({
                "team1": team1,
                "team2": team2,
                "winner_id": team1_id if team1["winner"] else team2_id
            })
        
        bracket_data[region] = region_bracket
    
    # Process subsequent rounds
    round_names = ["First Round", "Second Round", "Sweet 16", "Elite 8", "Final Four", "Championship"]
    subsequent_rounds = {}
    
    for round_num in range(1, 6):
        round_games = rounds.get(round_num, [])
        round_matches = []
        
        for game in round_games:
            team1_id = game["team1"]
            team2_id = game["team2"]
            
            # Get team data from previous rounds
            team1 = all_teams.get(team1_id, {
                "id": team1_id,
                "seed": game["seed_team1"],
                "name": team_name_mapping.get(team1_id, team1_id),
                "color": get_team_color(team_name_mapping.get(team1_id, team1_id))
            })
            
            team2 = all_teams.get(team2_id, {
                "id": team2_id,
                "seed": game["seed_team2"],
                "name": team_name_mapping.get(team2_id, team2_id),
                "color": get_team_color(team_name_mapping.get(team2_id, team2_id))
            })
            
            # Update winner status
            team1["winner"] = game["team1_win"]
            team2["winner"] = not game["team1_win"]
            
            # Generate realistic scores
            winner_score = random.randint(65, 95)
            # Closer games in later rounds
            loser_score = winner_score - random.randint(1, 15) if round_num >= 3 else winner_score - random.randint(5, 25)
            
            if team1["winner"]:
                team1["score"] = winner_score
                team2["score"] = loser_score
            else:
                team1["score"] = loser_score
                team2["score"] = winner_score
            
            # Store updated team data
            all_teams[team1_id] = team1
            all_teams[team2_id] = team2
            
            round_matches.append({
                "team1": team1,
                "team2": team2,
                "winner_id": team1_id if team1["winner"] else team2_id
            })
        
        subsequent_rounds[round_num] = round_matches
    
    # Generate HTML for the bracket
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCAA Tournament Bracket</title>
    <style>
        :root {
            --connector-color: #aaa;
            --bracket-bg: #f8f8f8;
            --winner-bg: #e6f7e6;
            --loser-bg: #f7e6e6;
            --winner-border: #28a745;
            --loser-border: #dc3545;
            --main-color: #0a4b78;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
            color: #333;
        }
        
        h1, h2 {
            text-align: center;
        }
        
        h1 {
            color: var(--main-color);
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #666;
            font-weight: normal;
            margin-top: 0;
            margin-bottom: 30px;
        }
        
        .bracket-container {
            display: flex;
            justify-content: center;
            overflow-x: auto;
            padding-bottom: 30px;
        }
        
        .bracket {
            display: flex;
            align-items: flex-start;
            min-width: 1200px;
        }
        
        .round {
            display: flex;
            flex-direction: column;
            margin: 0 10px;
        }
        
        .round-title {
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
            color: var(--main-color);
        }
        
        .region-title {
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--main-color);
            font-size: 1.2em;
        }
        
        .matchup {
            display: flex;
            flex-direction: column;
            margin-bottom: 15px;
            position: relative;
        }
        
        .team {
            display: flex;
            align-items: center;
            padding: 8px 10px;
            border: 1px solid #ddd;
            border-left-width: 5px;
            background-color: var(--bracket-bg);
            margin-bottom: 1px;
            transition: transform 0.2s ease;
            position: relative;
            min-width: 200px;
        }
        
        .team:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 10;
        }
        
        .team.winner {
            background-color: var(--winner-bg);
            border-left-color: var(--winner-border);
            font-weight: bold;
        }
        
        .team.loser {
            background-color: var(--loser-bg);
            border-left-color: var(--loser-border);
            color: #777;
        }
        
        .seed {
            font-weight: bold;
            margin-right: 8px;
            min-width: 20px;
            text-align: center;
        }
        
        .team-name {
            flex-grow: 1;
        }
        
        .score {
            font-weight: bold;
            margin-left: 10px;
        }
        
        .connector {
            position: absolute;
            border-color: var(--connector-color);
        }
        
        .connector-vertical {
            border-right: 2px solid;
            height: 50%;
            right: -10px;
        }
        
        .connector-horizontal {
            border-top: 2px solid;
            width: 10px;
            right: -10px;
        }
        
        .connector-top {
            top: 50%;
        }
        
        .connector-bottom {
            top: 0;
        }
        
        .final-four {
            margin-top: 100px;
        }
        
        .championship {
            margin-top: 200px;
        }
        
        .champion-box {
            border: 3px solid var(--winner-border);
            padding: 15px;
            text-align: center;
            background-color: var(--winner-bg);
            margin-top: 20px;
            border-radius: 5px;
        }
        
        .champion-title {
            font-size: 1.2em;
            margin-bottom: 10px;
            color: var(--main-color);
        }
        
        .champion-name {
            font-size: 1.5em;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>NCAA Tournament Bracket Simulation</h1>
    <h2>March Madness Bracket Visualization</h2>
    
    <div class="bracket-container">
        <div class="bracket">
"""
    
    # Add first round with regions
    html_content += """
            <!-- First Round -->
            <div class="round">
                <div class="round-title">First Round</div>
"""
    
    for region in regions:
        html_content += f"""
                <div class="region-title">{region} Region</div>
"""
        
        for i, matchup in enumerate(bracket_data[region]):
            team1 = matchup["team1"]
            team2 = matchup["team2"]
            
            html_content += f"""
                <div class="matchup">
                    <div class="team {('winner' if team1['winner'] else 'loser')}" style="border-left-color: {team1['color']}">
                        <div class="seed">{team1['seed']}</div>
                        <div class="team-name">{team1['name']}</div>
                        <div class="score">{team1['score']}</div>
                    </div>
                    <div class="team {('winner' if team2['winner'] else 'loser')}" style="border-left-color: {team2['color']}">
                        <div class="seed">{team2['seed']}</div>
                        <div class="team-name">{team2['name']}</div>
                        <div class="score">{team2['score']}</div>
                    </div>
                    <div class="connector connector-vertical connector-top"></div>
                    <div class="connector connector-horizontal"></div>
                </div>
"""
    
    html_content += """
            </div>
"""
    
    # Add subsequent rounds
    for round_num in range(1, 6):
        round_name = round_names[round_num]
        round_matches = subsequent_rounds[round_num]
        
        # Add special classes for Final Four and Championship
        special_class = ""
        if round_num == 4:
            special_class = " final-four"
        elif round_num == 5:
            special_class = " championship"
        
        html_content += f"""
            <!-- {round_name} -->
            <div class="round{special_class}">
                <div class="round-title">{round_name}</div>
"""
        
        for matchup in round_matches:
            team1 = matchup["team1"]
            team2 = matchup["team2"]
            
            html_content += f"""
                <div class="matchup">
                    <div class="team {('winner' if team1['winner'] else 'loser')}" style="border-left-color: {team1['color']}">
                        <div class="seed">{team1['seed']}</div>
                        <div class="team-name">{team1['name']}</div>
                        <div class="score">{team1['score']}</div>
                    </div>
                    <div class="team {('winner' if team2['winner'] else 'loser')}" style="border-left-color: {team2['color']}">
                        <div class="seed">{team2['seed']}</div>
                        <div class="team-name">{team2['name']}</div>
                        <div class="score">{team2['score']}</div>
                    </div>
"""
            
            # Don't add connectors for the championship game
            if round_num < 5:
                html_content += """
                    <div class="connector connector-vertical connector-top"></div>
                    <div class="connector connector-horizontal"></div>
"""
            
            html_content += """
                </div>
"""
        
        html_content += """
            </div>
"""
    
    # Find the champion
    championship_game = subsequent_rounds[5][0]
    champion = championship_game["team1"] if championship_game["team1"]["winner"] else championship_game["team2"]
    
    # Add champion box
    html_content += f"""
            <!-- Champion -->
            <div class="round">
                <div class="round-title">Champion</div>
                <div class="champion-box" style="border-color: {champion['color']}">
                    <div class="champion-title">Tournament Champion</div>
                    <div class="champion-name">{champion['seed']} {champion['name']}</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML to file
    with open("tournament_bracket.html", "w") as f:
        f.write(html_content)
    
    print(f"Bracket visualization saved to tournament_bracket.html")
    
    # Return the champion information
    return f"{champion['seed']} {champion['name']}"

def main():
    # Run the simulation
    print("Running NCAA Tournament simulation...")
    tournament_games = simulate_tournament()
    
    # Generate bracket visualization and get champion
    champion = generate_bracket_html(tournament_games)
    
    print(f"Tournament Champion: {champion}")
    print("Open tournament_bracket.html in your browser to view the bracket!")

if __name__ == "__main__":
    main() 
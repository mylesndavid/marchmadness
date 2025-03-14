import pandas as pd
import os

# Default colors for teams by seed
SEED_COLORS = {
    1: "#0066cc",  # Blue for 1 seeds
    2: "#009933",  # Green for 2 seeds
    3: "#cc3300",  # Red for 3 seeds
    4: "#9900cc",  # Purple for 4 seeds
    5: "#ff9900",  # Orange for 5 seeds
    6: "#669900",  # Olive for 6 seeds
    7: "#cc6600",  # Brown for 7 seeds
    8: "#0099cc",  # Light blue for 8 seeds
    9: "#ff6600",  # Dark orange for 9 seeds
    10: "#996633", # Brown for 10 seeds
    11: "#cc9900", # Gold for 11 seeds
    12: "#669999", # Teal for 12 seeds
    13: "#993366", # Maroon for 13 seeds
    14: "#666699", # Slate for 14 seeds
    15: "#999966", # Olive for 15 seeds
    16: "#666666"  # Gray for 16 seeds
}

def get_team_color(seed):
    """Get a consistent color for a team based on its seed"""
    seed_int = int(float(seed))
    return SEED_COLORS.get(seed_int, "#333333")

def generate_bracket_html(csv_file):
    """Generate HTML bracket visualization from tournament games in CSV file"""
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Group games by round
    rounds = {}
    for _, row in df.iterrows():
        round_num = row["tournament_round"]
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(row.to_dict())
    
    # Organize teams by region for the first round
    regions = ["East", "West", "South", "Midwest"]
    first_round = rounds[0]
    region_games = {region: [] for region in regions}
    
    # First round team ranges for each region
    region_ranges = {
        "East": range(1, 17),       # Teams 1-16
        "West": range(17, 33),      # Teams 17-32
        "South": range(33, 49),     # Teams 33-48
        "Midwest": range(49, 65)    # Teams 49-64
    }
    
    # Assign games to regions based on team IDs
    for game in first_round:
        team1_id = game["team1"]
        
        # Find which region this game belongs to
        assigned_region = None
        for region, id_range in region_ranges.items():
            if int(float(team1_id)) in id_range:
                assigned_region = region
                break
        
        if assigned_region:
            region_games[assigned_region].append(game)
    
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
            
            # Get odds directly from the CSV
            team1_odds = game["odds_team1"]
            team2_odds = 1.0 - team1_odds
            
            team1 = {
                "id": team1_id,
                "seed": game["seed_team1"],
                "name": f"Team {team1_id}",
                "color": get_team_color(game["seed_team1"]),
                "winner": game["team1_win"] == 1,
                "odds": team1_odds
            }
            
            team2 = {
                "id": team2_id,
                "seed": game["seed_team2"],
                "name": f"Team {team2_id}",
                "color": get_team_color(game["seed_team2"]),
                "winner": game["team1_win"] == 0,
                "odds": team2_odds
            }
            
            # Store teams for later rounds
            all_teams[team1_id] = team1
            all_teams[team2_id] = team2
            
            region_bracket.append({
                "team1": team1,
                "team2": team2,
                "winner_id": team1_id if team1["winner"] else team2_id,
                "team1_odds": team1_odds,
                "team2_odds": team2_odds
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
            
            # Get odds directly from the CSV for this specific matchup
            team1_odds = game["odds_team1"]
            team2_odds = 1.0 - team1_odds
            
            # Get team data from previous rounds
            team1 = all_teams.get(team1_id, {}).copy()
            team2 = all_teams.get(team2_id, {}).copy()
            
            # Update with current matchup data
            team1.update({
                "id": team1_id,
                "seed": game["seed_team1"],
                "name": f"Team {team1_id}",
                "color": get_team_color(game["seed_team1"]),
                "winner": game["team1_win"] == 1,
                "odds": team1_odds
            })
            
            team2.update({
                "id": team2_id,
                "seed": game["seed_team2"],
                "name": f"Team {team2_id}",
                "color": get_team_color(game["seed_team2"]),
                "winner": game["team1_win"] == 0,
                "odds": team2_odds
            })
            
            # Store updated team data
            all_teams[team1_id] = team1
            all_teams[team2_id] = team2
            
            round_matches.append({
                "team1": team1,
                "team2": team2,
                "winner_id": team1_id if team1["winner"] else team2_id,
                "team1_odds": team1_odds,
                "team2_odds": team2_odds
            })
        
        subsequent_rounds[round_num] = round_matches
    
    # Find the champion from the championship game
    championship_match = subsequent_rounds[5][0]
    champion_id = championship_match["team1"]["id"] if championship_match["team1"]["winner"] else championship_match["team2"]["id"]
    champion_id = str(float(champion_id))  # Ensure consistent format
    
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
            display: grid;
            grid-template-columns: repeat(3, 1fr) 1fr repeat(3, 1fr);
            grid-template-rows: auto;
            gap: 20px;
            min-width: 1400px;
            margin: 0 auto;
            align-items: center;
        }
        
        .region {
            display: flex;
            flex-direction: column;
        }
        
        .east-region {
            grid-column: 1;
            grid-row: 1;
        }
        
        .west-region {
            grid-column: 1;
            grid-row: 2;
        }
        
        .south-region {
            grid-column: 7;
            grid-row: 1;
        }
        
        .midwest-region {
            grid-column: 7;
            grid-row: 2;
        }
        
        .east-rounds, .west-rounds, .south-rounds, .midwest-rounds {
            display: flex;
            height: 100%;
        }
        
        .east-rounds {
            grid-column: 2;
            grid-row: 1;
            flex-direction: row;
        }
        
        .west-rounds {
            grid-column: 2;
            grid-row: 2;
            flex-direction: row;
        }
        
        .south-rounds {
            grid-column: 6;
            grid-row: 1;
            flex-direction: row-reverse;
        }
        
        .midwest-rounds {
            grid-column: 6;
            grid-row: 2;
            flex-direction: row-reverse;
        }
        
        .final-four {
            grid-column: 3 / span 3;
            grid-row: 1 / span 2;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .round {
            display: flex;
            flex-direction: column;
            margin: 0 10px;
            min-width: 250px;
            justify-content: space-around;
            height: 100%;
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
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
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
        
        .team.champion-path {
            background-color: #fff2cc;
            border-left-color: #ffd700;
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
        
        .odds {
            font-weight: bold;
            margin-left: 10px;
            color: #555;
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
        
        .champion-box {
            border: 3px solid var(--winner-border);
            padding: 15px;
            text-align: center;
            background-color: var(--winner-bg);
            margin-top: 20px;
            border-radius: 5px;
            max-width: 300px;
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
        
        .final-four-matchups {
            display: flex;
            flex-direction: column;
            gap: 50px;
            margin-bottom: 50px;
        }
        
        .championship-matchup {
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <h1>NCAA Tournament Bracket Simulation</h1>
    <h2>March Madness Bracket Visualization</h2>
    
    <div class="bracket-container">
        <div class="bracket">
"""
    
    # Add regions with first round
    for i, region in enumerate(["East", "West"]):
        region_class = region.lower() + "-region"
        html_content += f"""
            <div class="{region_class}">
                <div class="region-title">{region} Region</div>
                <div class="round">
                    <div class="round-title">First Round</div>
"""
        
        for matchup in bracket_data[region]:
            team1 = matchup["team1"]
            team2 = matchup["team2"]
            
            html_content += f"""
                    <div class="matchup">
                        <div class="team {('winner' if team1['winner'] else 'loser')} {('champion-path' if str(float(team1['id'])) == champion_id else '')}" style="border-left-color: {team1['color']}">
                            <div class="seed">{team1['seed']}</div>
                            <div class="team-name">{team1['name']}</div>
                            <div class="odds">{team1['odds']:.3f}</div>
                        </div>
                        <div class="team {('winner' if team2['winner'] else 'loser')} {('champion-path' if str(float(team2['id'])) == champion_id else '')}" style="border-left-color: {team2['color']}">
                            <div class="seed">{team2['seed']}</div>
                            <div class="team-name">{team2['name']}</div>
                            <div class="odds">{team2['odds']:.3f}</div>
                        </div>
                    </div>
"""
        
        html_content += """
                </div>
            </div>
"""
        
        # Add subsequent rounds for this region
        rounds_class = region.lower() + "-rounds"
        html_content += f"""
            <div class="{rounds_class}">
"""
        
        # Add rounds 1-3 (Second Round, Sweet 16, Elite 8)
        for round_num in range(1, 4):
            round_name = round_names[round_num]
            round_matches = [m for m in subsequent_rounds[round_num] if any([
                int(float(m["team1"]["id"])) in region_ranges[region],
                int(float(m["team2"]["id"])) in region_ranges[region]
            ])]
            
            html_content += f"""
                <div class="round">
                    <div class="round-title">{round_name}</div>
"""
            
            for matchup in round_matches:
                team1 = matchup["team1"]
                team2 = matchup["team2"]
                
                # Only include matchups that belong to this region
                if not any([int(float(team1["id"])) in region_ranges[region], 
                           int(float(team2["id"])) in region_ranges[region]]):
                    continue
                
                html_content += f"""
                    <div class="matchup">
                        <div class="team {('winner' if team1['winner'] else 'loser')} {('champion-path' if str(float(team1['id'])) == champion_id else '')}" style="border-left-color: {team1['color']}">
                            <div class="seed">{team1['seed']}</div>
                            <div class="team-name">{team1['name']}</div>
                            <div class="odds">{team1['odds']:.3f}</div>
                        </div>
                        <div class="team {('winner' if team2['winner'] else 'loser')} {('champion-path' if str(float(team2['id'])) == champion_id else '')}" style="border-left-color: {team2['color']}">
                            <div class="seed">{team2['seed']}</div>
                            <div class="team-name">{team2['name']}</div>
                            <div class="odds">{team2['odds']:.3f}</div>
                        </div>
                    </div>
"""
            
            html_content += """
                </div>
"""
        
        html_content += """
            </div>
"""
    
    # Add South and Midwest regions
    for i, region in enumerate(["South", "Midwest"]):
        region_class = region.lower() + "-region"
        html_content += f"""
            <div class="{region_class}">
                <div class="region-title">{region} Region</div>
                <div class="round">
                    <div class="round-title">First Round</div>
"""
        
        for matchup in bracket_data[region]:
            team1 = matchup["team1"]
            team2 = matchup["team2"]
            
            html_content += f"""
                    <div class="matchup">
                        <div class="team {('winner' if team1['winner'] else 'loser')} {('champion-path' if str(float(team1['id'])) == champion_id else '')}" style="border-left-color: {team1['color']}">
                            <div class="seed">{team1['seed']}</div>
                            <div class="team-name">{team1['name']}</div>
                            <div class="odds">{team1['odds']:.3f}</div>
                        </div>
                        <div class="team {('winner' if team2['winner'] else 'loser')} {('champion-path' if str(float(team2['id'])) == champion_id else '')}" style="border-left-color: {team2['color']}">
                            <div class="seed">{team2['seed']}</div>
                            <div class="team-name">{team2['name']}</div>
                            <div class="odds">{team2['odds']:.3f}</div>
                        </div>
                    </div>
"""
        
        html_content += """
                </div>
            </div>
"""
        
        # Add subsequent rounds for this region
        rounds_class = region.lower() + "-rounds"
        html_content += f"""
            <div class="{rounds_class}">
"""
        
        # Add rounds 1-3 (Second Round, Sweet 16, Elite 8)
        for round_num in range(1, 4):
            round_name = round_names[round_num]
            round_matches = [m for m in subsequent_rounds[round_num] if any([
                int(float(m["team1"]["id"])) in region_ranges[region],
                int(float(m["team2"]["id"])) in region_ranges[region]
            ])]
            
            html_content += f"""
                <div class="round">
                    <div class="round-title">{round_name}</div>
"""
            
            for matchup in round_matches:
                team1 = matchup["team1"]
                team2 = matchup["team2"]
                
                # Only include matchups that belong to this region
                if not any([int(float(team1["id"])) in region_ranges[region], 
                           int(float(team2["id"])) in region_ranges[region]]):
                    continue
                
                html_content += f"""
                    <div class="matchup">
                        <div class="team {('winner' if team1['winner'] else 'loser')} {('champion-path' if str(float(team1['id'])) == champion_id else '')}" style="border-left-color: {team1['color']}">
                            <div class="seed">{team1['seed']}</div>
                            <div class="team-name">{team1['name']}</div>
                            <div class="odds">{team1['odds']:.3f}</div>
                        </div>
                        <div class="team {('winner' if team2['winner'] else 'loser')} {('champion-path' if str(float(team2['id'])) == champion_id else '')}" style="border-left-color: {team2['color']}">
                            <div class="seed">{team2['seed']}</div>
                            <div class="team-name">{team2['name']}</div>
                            <div class="odds">{team2['odds']:.3f}</div>
                        </div>
                    </div>
"""
            
            html_content += """
                </div>
"""
        
        html_content += """
            </div>
"""
    
    # Add Final Four and Championship
    html_content += """
            <div class="final-four">
                <div class="region-title">Final Four</div>
                <div class="final-four-matchups">
"""
    
    # Final Four matchups
    final_four_matches = subsequent_rounds[4]
    for matchup in final_four_matches:
        team1 = matchup["team1"]
        team2 = matchup["team2"]
        
        # Determine regions for Final Four teams
        team1_region = "Unknown"
        team2_region = "Unknown"
        for region, id_range in region_ranges.items():
            if int(float(team1["id"])) in id_range:
                team1_region = region
            if int(float(team2["id"])) in id_range:
                team2_region = region
        
        html_content += f"""
                    <div class="matchup">
                        <div class="team {('winner' if team1['winner'] else 'loser')} {('champion-path' if str(float(team1['id'])) == champion_id else '')}" style="border-left-color: {team1['color']}">
                            <div class="seed">{team1['seed']}</div>
                            <div class="team-name">{team1['name']} ({team1_region})</div>
                            <div class="odds">{team1['odds']:.3f}</div>
                        </div>
                        <div class="team {('winner' if team2['winner'] else 'loser')} {('champion-path' if str(float(team2['id'])) == champion_id else '')}" style="border-left-color: {team2['color']}">
                            <div class="seed">{team2['seed']}</div>
                            <div class="team-name">{team2['name']} ({team2_region})</div>
                            <div class="odds">{team2['odds']:.3f}</div>
                        </div>
                    </div>
"""
    
    html_content += """
                </div>
                
                <div class="region-title">Championship</div>
                <div class="championship-matchup">
"""
    
    # Championship matchup
    championship_match = subsequent_rounds[5][0]
    team1 = championship_match["team1"]
    team2 = championship_match["team2"]
    
    # Determine regions for Championship teams
    team1_region = "Unknown"
    team2_region = "Unknown"
    for region, id_range in region_ranges.items():
        if int(float(team1["id"])) in id_range:
            team1_region = region
        if int(float(team2["id"])) in id_range:
            team2_region = region
    
    html_content += f"""
                    <div class="matchup">
                        <div class="team {('winner' if team1['winner'] else 'loser')} {('champion-path' if str(float(team1['id'])) == champion_id else '')}" style="border-left-color: {team1['color']}">
                            <div class="seed">{team1['seed']}</div>
                            <div class="team-name">{team1['name']} ({team1_region})</div>
                            <div class="odds">{team1['odds']:.3f}</div>
                        </div>
                        <div class="team {('winner' if team2['winner'] else 'loser')} {('champion-path' if str(float(team2['id'])) == champion_id else '')}" style="border-left-color: {team2['color']}">
                            <div class="seed">{team2['seed']}</div>
                            <div class="team-name">{team2['name']} ({team2_region})</div>
                            <div class="odds">{team2['odds']:.3f}</div>
                        </div>
                    </div>
"""
    
    # Find the champion
    champion = team1 if team1["winner"] else team2
    champion_region = team1_region if team1["winner"] else team2_region
    
    # Add champion box
    html_content += f"""
                    <div class="champion-box" style="border-color: {champion['color']}">
                        <div class="champion-title">Tournament Champion</div>
                        <div class="champion-name">Seed {champion['seed']} - {champion['name']} ({champion_region})</div>
                    </div>
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
    
    # Return the champion information
    return f"Seed {champion['seed']} - {champion['name']} ({champion_region})"

def main():
    # Check if the CSV file exists
    csv_file = "bracket_results.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run the bracket.py script first.")
        return
    
    # Generate bracket visualization from CSV
    print(f"Generating bracket visualization from {csv_file}...")
    champion = generate_bracket_html(csv_file)
    
    print(f"Tournament Champion: {champion}")
    print("Open tournament_bracket.html in your browser to view the bracket!")

if __name__ == "__main__":
    main() 
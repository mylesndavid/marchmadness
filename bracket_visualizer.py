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
    
    # Create bracket data structure for visualization
    bracket_data = {
        "teams": [],
        "results": [[] for _ in range(6)]  # 6 rounds total
    }
    
    # Process each region
    for region in regions:
        region_first_round = region_games.get(region, [])
        region_teams = []
        
        # Add first round matchups to teams array
        for game in region_first_round:
            team1_name = team_name_mapping.get(game["team1"], game["team1"])
            team2_name = team_name_mapping.get(game["team2"], game["team2"])
            
            team1 = {"seed": game["seed_team1"], "name": team1_name}
            team2 = {"seed": game["seed_team2"], "name": team2_name}
            
            # Add team pair to bracket data
            region_teams.append([
                format_team_name(team1, team_name_mapping),
                format_team_name(team2, team_name_mapping)
            ])
            
            # Add result to first round results
            winner_score = random.randint(65, 95)  # More realistic score range
            loser_score = winner_score - random.randint(5, 25)  # Score differential
            
            if game["team1_win"]:
                bracket_data["results"][0].append([winner_score, loser_score])
            else:
                bracket_data["results"][0].append([loser_score, winner_score])
        
        # Add region teams to overall bracket
        bracket_data["teams"].extend(region_teams)
    
    # Process subsequent rounds
    for round_num in range(1, 6):
        round_games = rounds.get(round_num, [])
        
        for game in round_games:
            team1_win = game["team1_win"]
            
            # Generate realistic scores
            winner_score = random.randint(65, 95)
            loser_score = winner_score - random.randint(5, 25)
            
            # Closer games in later rounds
            if round_num >= 3:  # Sweet 16 and beyond
                loser_score = winner_score - random.randint(1, 15)
            
            if team1_win:
                bracket_data["results"][round_num].append([winner_score, loser_score])
            else:
                bracket_data["results"][round_num].append([loser_score, winner_score])
    
    # Generate team colors for CSS
    team_color_css = ""
    for team_id, team_name in team_name_mapping.items():
        color = get_team_color(team_name)
        for seed in range(1, 17):
            team_color_css += f".team[data-teamid='{seed} {team_name}'] {{ background-color: {color}; color: white; }}\n"
    
    # Create HTML file with bracket visualization
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NCAA Tournament Bracket</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-bracket/1.3.2/jquery.bracket.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-bracket/1.3.2/jquery.bracket.min.js"></script>
  <style>
    body {{
      font-family: 'Helvetica Neue', Arial, sans-serif;
      text-align: center;
      background-color: #f4f4f4;
      padding: 20px;
      color: #333;
    }}
    
    h1 {{
      color: #0a4b78;
      font-size: 2.5em;
      margin-bottom: 10px;
    }}
    
    h2 {{
      color: #666;
      font-weight: normal;
      margin-top: 0;
      margin-bottom: 30px;
    }}
    
    .bracket-container {{
      display: flex;
      justify-content: center;
      margin-top: 30px;
      overflow-x: auto;
      width: 100%;
      padding-bottom: 30px;
    }}
    
    #tournament {{
      min-width: 1200px;
    }}
    
    .jQBracket .team {{
      background-color: #f8f8f8;
      border: 1px solid #ddd;
      border-left: 5px solid #ddd;
      transition: all 0.2s ease;
    }}
    
    .jQBracket .team.win {{
      background-color: #e6f7e6;
      border-left: 5px solid #28a745;
      font-weight: bold;
    }}
    
    .jQBracket .team.lose {{
      background-color: #f7e6e6;
      border-left: 5px solid #dc3545;
      color: #999;
    }}
    
    .jQBracket .team:hover {{
      transform: translateX(5px);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    
    .jQBracket .connector {{
      border-color: #aaa;
    }}
    
    .jQBracket .label {{
      color: #0a4b78;
      font-weight: bold;
    }}
    
    .round-labels {{
      display: flex;
      justify-content: space-around;
      margin: 20px auto;
      max-width: 1200px;
      font-weight: bold;
      color: #0a4b78;
    }}
    
    .region-labels {{
      display: flex;
      justify-content: space-around;
      margin: 0 auto 20px;
      max-width: 1200px;
    }}
    
    .region-label {{
      width: 25%;
      font-weight: bold;
      color: #0a4b78;
      font-size: 1.2em;
    }}
    
    /* Team-specific colors */
    {team_color_css}
  </style>
</head>
<body>
  <h1>NCAA Tournament Bracket Simulation</h1>
  <h2>March Madness Bracket Visualization</h2>
  
  <div class="round-labels">
    <div>First Round</div>
    <div>Second Round</div>
    <div>Sweet 16</div>
    <div>Elite 8</div>
    <div>Final Four</div>
    <div>Championship</div>
  </div>
  
  <div class="region-labels">
    <div class="region-label">East Region</div>
    <div class="region-label">West Region</div>
    <div class="region-label">South Region</div>
    <div class="region-label">Midwest Region</div>
  </div>
  
  <div class="bracket-container">
    <div id="tournament"></div>
  </div>
  
  <script>
    $(document).ready(function() {{
      var bracketData = {json.dumps(bracket_data)};
      
      $('#tournament').bracket({{
        init: bracketData,
        teamWidth: 200,
        scoreWidth: 40,
        matchMargin: 30,
        roundMargin: 50,
        skipConsolationRound: true,
        disableToolbar: true,
        skipSecondaryFinal: true,
        centerConnectors: true,
        onMatchClick: function(data) {{
          console.log(data);
        }},
        decorator: {{
          edit: function() {{ /* No edit function needed */ }},
          render: function(container, data, score, state) {{
            container.append(data);
            container.attr('data-teamid', data);
            
            if (score) {{
              container.append('<span class="score">' + score + '</span>');
            }}
            
            switch(state) {{
              case "win":
                container.addClass("win");
                break;
              case "lose":
                container.addClass("lose");
                break;
            }}
          }}
        }}
      }});
    }});
  </script>
</body>
</html>
"""
    
    # Write HTML to file
    with open("tournament_bracket.html", "w") as f:
        f.write(html_content)
    
    print(f"Bracket visualization saved to tournament_bracket.html")
    
    # Return the champion information
    championship_game = [g for g in tournament_games if g["tournament_round"] == 5][0]
    if championship_game["team1_win"]:
        champion_id = championship_game["team1"]
        champion_seed = championship_game["seed_team1"]
    else:
        champion_id = championship_game["team2"]
        champion_seed = championship_game["seed_team2"]
    
    champion_name = team_name_mapping.get(champion_id, champion_id)
    return f"{champion_seed} {champion_name}"

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
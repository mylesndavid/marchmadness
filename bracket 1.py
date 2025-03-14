from calculate_odds import get_win, get_odds
from collections import defaultdict
from collections import Counter
import pandas as pd
import random  # Added for random day assignment

def create_tournament():
    regions = ["East", "West", "South", "Midwest"]
    teams = []
    team_id = 1
    
    for region in regions:
        for seed in range(1, 17):
            teams.append({
                "region": region,
                "seed": seed,
                "name": str(team_id)
            })
            team_id += 1
    
    return teams

def create_region_matchups(teams):
    # Create a lookup by seed
    by_seed = {team["seed"]: team for team in teams}
    
    # Create matchups in the standard bracket format
    matchups = [
        {"team1": by_seed[1], "team2": by_seed[16]},  # 1 vs 16
        {"team1": by_seed[8], "team2": by_seed[9]},   # 8 vs 9
        {"team1": by_seed[5], "team2": by_seed[12]},  # 5 vs 12
        {"team1": by_seed[4], "team2": by_seed[13]},  # 4 vs 13
        {"team1": by_seed[6], "team2": by_seed[11]},  # 6 vs 11
        {"team1": by_seed[3], "team2": by_seed[14]},  # 3 vs 14
        {"team1": by_seed[7], "team2": by_seed[10]},  # 7 vs 10
        {"team1": by_seed[2], "team2": by_seed[15]}   # 2 vs 15
    ]
    
    return matchups

def simulate_matchup(matchup, tournament_round):
    team1 = matchup["team1"]
    team2 = matchup["team2"]
    
    winning_seed = get_win(team1["seed"], team2["seed"], tournament_round)
    winner = team1 if winning_seed == team1["seed"] else team2
    loser = team2 if winner == team1 else team1
    
    # Calculate odds of team1 winning
    team1_win_odds = get_odds(team1["seed"], team2["seed"], tournament_round)
    # Record if team1 won (1) or lost (0)
    team1_win = 1 if winner == team1 else 0
    
    return {
        "team1": team1,
        "team2": team2,
        "winner": winner,
        "loser": loser,
        "team1_seed": team1["seed"],
        "team2_seed": team2["seed"],
        "team1_win_odds": team1_win_odds,
        "team1_win": team1_win
    }

def simulate_round(matchups, tournament_round, days=1):
    results = []
    games = []
    
    # If there are two days, create balanced day assignments
    if days == 2:
        num_matchups = len(matchups)
        # Create a balanced list of day assignments
        day_assignments = [1] * (num_matchups // 2) + [2] * (num_matchups - num_matchups // 2)
        # Shuffle the day assignments
        random.shuffle(day_assignments)
    
    for idx, matchup in enumerate(matchups):
        result = simulate_matchup(matchup, tournament_round)
        results.append(result)
        team1 = result["team1"]
        team2 = result["team2"]
        winner = result["winner"]
        loser = result["loser"]
        
        # Assign day based on number of days in the round
        if days == 1:
            day = 1
        else:
            day = day_assignments[idx]
        
        # Create game entry for the returned data structure
        game_data = {
            "team1": team1["name"],
            "team2": team2["name"],
            "seed_team1": team1["seed"],
            "seed_team2": team2["seed"],
            "odds_team1": result["team1_win_odds"],
            "team1_win": result["team1_win"],
            "tournament_round": tournament_round,
            "day": day  # Add day information to game data
        }
        games.append(game_data)
        
        # print(f"{team1['name']} (Seed {team1['seed']}) vs {team2['name']} (Seed {team2['seed']}) => {winner['name']} defeats {loser['name']}")
    
    return results, games

def create_next_round(results):
    next_matchups = []
    
    for i in range(0, len(results), 2):
        if i + 1 < len(results):
            next_matchups.append({
                "team1": results[i]["winner"],
                "team2": results[i+1]["winner"]
            })
    
    return next_matchups

def simulate_tournament():
    # Create initial 64 teams
    teams = create_tournament()
    
    # Group teams by region
    regions = {}
    for team in teams:
        region = team["region"]
        if region not in regions:
            regions[region] = []
        regions[region].append(team)
    
    # Track all games across the tournament
    all_games = []
    
    # Simulate rounds within each region
    region_winners = []
    for region_name, region_teams in regions.items():
        # print(f"\n=== {region_name} Region ===")
        
        # First Round (8 matchups) - 2 days
        matchups = create_region_matchups(region_teams)
        first_round_results, first_round_games = simulate_round(matchups, 0, days=2)
        all_games.extend(first_round_games)
        
        # Second Round (4 matchups) - 2 days
        second_round_matchups = create_next_round(first_round_results)
        second_round_results, second_round_games = simulate_round(second_round_matchups, 1, days=2)
        all_games.extend(second_round_games)
        
        # Sweet 16 (2 matchups) - 2 days
        sweet16_matchups = create_next_round(second_round_results)
        sweet16_results, sweet16_games = simulate_round(sweet16_matchups, 2, days=2)
        all_games.extend(sweet16_games)
        
        # Elite 8 (1 matchup - determines region winner) - initially assign day 1 to all
        elite8_matchups = create_next_round(sweet16_results)
        elite8_results, elite8_games = simulate_round(elite8_matchups, 3, days=1)
        all_games.extend(elite8_games)
        
        # Save the region winner
        region_winner = elite8_results[0]["winner"]
        region_winners.append(region_winner)
    
    # Post-process Elite 8 games to balance across 2 days
    # Find all Elite 8 games
    elite8_indices = [i for i, game in enumerate(all_games) if game["tournament_round"] == 3]
    
    # Assign 2 games to day 1 and 2 games to day 2
    for i, idx in enumerate(elite8_indices):
        if i < 2:  # First two games
            all_games[idx]["day"] = 1
        else:      # Last two games
            all_games[idx]["day"] = 2
    
    # Final Four - 1 day
    final_four_matchups = [
        {"team1": region_winners[0], "team2": region_winners[1]},
        {"team1": region_winners[2], "team2": region_winners[3]}
    ]
    final_four_results, final_four_games = simulate_round(final_four_matchups, 4, days=1)
    all_games.extend(final_four_games)
    
    # Championship Game - 1 day
    championship_matchup = create_next_round(final_four_results)
    championship_result, championship_games = simulate_round(championship_matchup, 5, days=1)
    all_games.extend(championship_games)
    
    # Tournament Champion
    champion = championship_result[0]["winner"]
    
    return all_games

def main():
    print("NCAA March Madness Tournament Simulation")
    print("=======================================")
    tournament_games = simulate_tournament()
    print("\nSimulation complete!")
    print(f"Total games recorded: {len(tournament_games)}")
    
    print(tournament_games[-1])

    # Convert tournament_games to a DataFrame
    # df = pd.DataFrame(tournament_games)
    # df.to_csv('results.csv', index=False)


    # num_simulations = 1000
    # final_winners = []

    # for _ in range(num_simulations):
    #     tournament_games = simulate_tournament()
    #     final_winner = tournament_games[-1]["seed_team1"] if tournament_games[-1]["team1_win"] else tournament_games[-1]["seed_team2"]
    #     final_winners.append(final_winner)

    # win_counts = Counter(final_winners)
    # print("\nWin counts by seed after 1000 simulations:")
    # for seed, count in sorted(win_counts.items()):
    #     print(f"Seed {seed}: {count} wins")


if __name__ == "__main__":
    main()
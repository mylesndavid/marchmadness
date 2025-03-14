import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd


class MarchMadnessEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, teams_df=None, historical_df=None, num_entries=5, render_mode=None):
        super(MarchMadnessEnv, self).__init__()

        self.num_teams = 64
        self.num_matches = 63  # Total number of matches
        self.num_entries = num_entries  # Fixed to 5 entries per participant
        self.render_mode = render_mode

        # Define action space: Each entry selects one team (0-63)
        self.action_space = spaces.MultiDiscrete([self.num_teams] * num_entries)
        
        # Define observation space - simplified without action masking
        self.observation_space = spaces.Dict({
            'teams_status': spaces.Box(
                low=np.array([[0, 1, -1000, 0]] * self.num_teams),
                high=np.array([[1, 16, 1000, self.num_matches]] * self.num_teams),
                dtype=np.float32
            )
        })

        # Initialize team state
        if teams_df is not None:
            self.original_teams_df = teams_df.copy()
            self.teams_df = teams_df.copy()
            self.update_teams_state(teams_df)
        else:
            raise ValueError("Please provide a teams DataFrame.")
        
        # Per-entry tracking
        self.current_match = np.zeros(num_entries, dtype=int)
        self.done = np.zeros(num_entries, dtype=bool)
        self.champion = [None] * num_entries
        self.action_history = [[] for _ in range(num_entries)]
        self.used_teams = [set() for _ in range(num_entries)]
        
        # Track all selections for each entry
        self.last_attempted_team = [None] * num_entries
        self.last_selection_valid = [None] * num_entries
        self.last_selection_reason = [None] * num_entries
        
        # Store ALL selections made by each entry (valid or not)
        self.all_selections = [[] for _ in range(num_entries)]
        
        # Initialize matches
        self.matches = self._generate_matches_from_df(teams_df)
        
        # Initialize historical DataFrame
        if historical_df is not None:
            self.historical_df = historical_df.copy()
            self._process_historical_df()
        else:
            self._init_historical_df()
    
    def _init_historical_df(self):
        """Initialize an empty historical selections DataFrame"""
        self.historical_df = pd.DataFrame({
            'entry_id': [],
            'team_id': [],
            'match_no': [],
            'valid': []
        })

    def _process_historical_df(self):
        """Process historical DataFrame to update used teams for each entry"""
        if self.historical_df.empty:
            return
            
        # Group by entry_id and collect used teams
        for entry_id in range(self.num_entries):
            entry_data = self.historical_df[self.historical_df['entry_id'] == entry_id]
            if not entry_data.empty:
                # Add teams to all_selections
                for _, row in entry_data.iterrows():
                    try:
                        team_id = int(row['team_id'])  # Convert to integer
                        is_valid = bool(row.get('valid', True))  # Default to True if 'valid' column doesn't exist
                        
                        # Add to selection history
                        self.all_selections[entry_id].append(team_id)
                        
                        # Only mark as used if it was a valid selection
                        if is_valid:
                            self.used_teams[entry_id].add(team_id)

                            # Update current match count
                            match_no = int(row.get('match_no', -1))
                            if match_no > 0:
                                self.current_match[entry_id] += 1
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Error processing historical data - {e}")
                        continue
    
    def update_historical_df(self, historical_df):
        """Update the historical selections and internal state from a DataFrame"""
        if historical_df is None or historical_df.empty:
            return
            
        # Store the DataFrame
        self.historical_df = historical_df.copy()
        
        # Reset entry tracking that depends on history
        for entry_id in range(self.num_entries):
            self.used_teams[entry_id] = set()
            self.all_selections[entry_id] = []
            self.current_match[entry_id] = 0
            self.action_history[entry_id] = []
        
        # Process the historical data to update state
        for _, row in historical_df.iterrows():
            try:
                entry_id = int(row['entry_id'])
                team_id = int(row['team_id'])
                match_no = int(row.get('match_no', -1))
                is_valid = bool(row.get('valid', True))
                
                if entry_id < self.num_entries and team_id < self.num_teams:  # Ensure IDs are valid
                    # Add to selections history
                    self.all_selections[entry_id].append(team_id)
                    
                    # If valid, add to used teams
                    if is_valid:
                        self.used_teams[entry_id].add(team_id)
                        
                        # If it has a match number, it was a successful selection
                        if match_no > 0:
                            # Find the loser for this match
                            for team1, team2 in self.matches:
                                if (team1 == team_id or team2 == team_id) and match_no-1 < len(self.matches):
                                    loser = team2 if team1 == team_id else team1
                                    
                                    # Record in action history
                                    self.action_history[entry_id].append({
                                        'match': match_no,
                                        'winner': team_id,
                                        'loser': loser,
                                        'winner_name': self.team_names[team_id] if hasattr(self, 'team_names') else f'Team_{team_id}',
                                        'loser_name': self.team_names[loser] if hasattr(self, 'team_names') else f'Team_{loser}'
                                    })
                                    
                                    # Mark loser as unavailable
                                    self.available_teams[loser] = 0
                                    break
                            
                            # Increment match counter for valid selections
                            self.current_match[entry_id] += 1
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing historical data row - {e}")
                continue

        # Check for champions
        for entry_id in range(self.num_entries):
            if self.current_match[entry_id] >= self.num_matches:
                self.done[entry_id] = True
                if self.action_history[entry_id]:
                    self.champion[entry_id] = self.action_history[entry_id][-1]['winner']
    
    def _generate_matches_from_df(self, df):
        """Generate match pairings from the DataFrame"""
        if len(df) != self.num_teams:
            raise ValueError(f"DataFrame must have exactly {self.num_teams} rows.")
        
        matches = []
        match_numbers = df['match no'].fillna(0).to_numpy(dtype=int)
        available = df['playable'].to_numpy(dtype=int)
        
        # Create a mapping from match number to teams
        match_dict = {}
        for team_idx, match_num in enumerate(match_numbers):
            if match_num > 0 and available[team_idx]:
                if match_num not in match_dict:
                    match_dict[match_num] = []
                match_dict[match_num].append(team_idx)
        
        # Validate and sort matches
        for match_num in sorted(match_dict.keys()):
            if len(match_dict[match_num]) == 2:
                matches.append((match_dict[match_num][0], match_dict[match_num][1]))
            else:
                print(f"Warning: Match {match_num} doesn't have exactly 2 teams.")
        
        return matches

    def update_teams_state(self, df):
        """Update the environment's state using a teams DataFrame"""
        if len(df) != self.num_teams:
            raise ValueError(f"Teams DataFrame must have exactly {self.num_teams} rows.")
        
        self.teams_df = df.copy()
        self.seeds = df['teamseed'].to_numpy(dtype=int)
        self.available_teams = df['playable'].to_numpy(dtype=int)
        self.odds = df['odds'].to_numpy(dtype=float)
        self.team_names = df.get('teamname', pd.Series([f'Team_{i}' for i in range(self.num_teams)])).tolist()

    def get_observation(self):
        """Get the current observation"""
        # Create teams status array [playable, seed, odds, match_no]
        teams_status = np.zeros((self.num_teams, 4), dtype=np.float32)
        teams_status[:, 0] = self.available_teams
        teams_status[:, 1] = self.seeds
        teams_status[:, 2] = self.odds
        
        # Add match numbers
        match_assignments = np.zeros(self.num_teams)
        for idx, (team1, team2) in enumerate(self.matches):
            if self.available_teams[team1] and self.available_teams[team2]:
                match_assignments[team1] = idx + 1
                match_assignments[team2] = idx + 1
        teams_status[:, 3] = match_assignments
        
        return {
            'teams_status': teams_status
        }

    def step(self, actions):
        """
        Take a step in the environment
        
        Args:
            actions: List of team IDs selected by each entry
            
        Returns:
            observation: Updated observation
            reward: Reward for this step
            terminated: Whether episode is done
            truncated: Whether episode was truncated
            info: Additional info
        """
        # Convert to list if needed
        if isinstance(actions, (int, np.integer)):
            actions = [actions]
        if isinstance(actions, np.ndarray):
            actions = actions.tolist()
        
        # Convert actions to integers
        try:
            actions = [int(a) for a in actions]
        except (ValueError, TypeError):
            raise ValueError("Actions must be convertible to integers")
        
        if len(actions) != self.num_entries:
            raise ValueError(f"Expected {self.num_entries} actions, got {len(actions)}")
        
        # Process each entry's selection
        rewards = np.zeros(self.num_entries)
        infos = {'entries': [{} for _ in range(self.num_entries)]}
        historical_entries = []
        
        # Reset tracking for this step
        self.last_attempted_team = list(actions)  # Store all attempted selections
        self.last_selection_valid = [False] * self.num_entries
        self.last_selection_reason = [""] * self.num_entries
        
        for entry_id, team in enumerate(actions):
            # Ensure team is within valid range
            if team < 0 or team >= self.num_teams:
                team = team % self.num_teams  # Wrap around if out of range
            
            # Add team to selection history regardless of validity
            self.all_selections[entry_id].append(team)
            
            # Record the attempt for rendering
            team_name = self.team_names[team] if hasattr(self, 'team_names') else f'Team_{team}'
            infos['entries'][entry_id]['selected_team'] = team
            infos['entries'][entry_id]['selected_team_name'] = team_name
            
            # Skip if entry is done
            if self.done[entry_id]:
                infos['entries'][entry_id]['status'] = 'done'
                self.last_selection_reason[entry_id] = "Entry already completed"
                
                # Record in historical DataFrame even if invalid
                historical_entries.append({
                    'entry_id': entry_id,
                    'team_id': team,
                    'match_no': -1,
                    'valid': False
                })
                continue
            
            # Initialize info
            is_in_match = False
            is_playable = self.available_teams[team] == 1
            is_used = team in self.used_teams[entry_id]
            
            # Find the match involving this team
            match_idx = None
            for idx, (team1, team2) in enumerate(self.matches):
                if (team == team1 or team == team2) and self.available_teams[team1] and self.available_teams[team2]:
                    match_idx = idx
                    is_in_match = True
                    break
            
            infos['entries'][entry_id]['is_in_match'] = is_in_match
            infos['entries'][entry_id]['is_playable'] = is_playable
            infos['entries'][entry_id]['is_used'] = is_used
            
            # Determine why selection is invalid, if it is
            if not is_playable:
                self.last_selection_reason[entry_id] = "Team not playable"
                infos['entries'][entry_id]['processed'] = False
                
                # Record in historical DataFrame even if invalid
                historical_entries.append({
                    'entry_id': entry_id,
                    'team_id': team,
                    'match_no': -1,
                    'valid': False
                })
                continue
                
            if not is_in_match:
                self.last_selection_reason[entry_id] = "Team not in an active match"
                infos['entries'][entry_id]['processed'] = False
                
                # Record in historical DataFrame even if invalid
                historical_entries.append({
                    'entry_id': entry_id,
                    'team_id': team,
                    'match_no': -1,
                    'valid': False
                })
                continue
                
            if is_used:
                self.last_selection_reason[entry_id] = "Team already used by this entry"
                infos['entries'][entry_id]['processed'] = False
                
                # Record in historical DataFrame even if invalid
                historical_entries.append({
                    'entry_id': entry_id,
                    'team_id': team,
                    'match_no': -1,
                    'valid': False
                })
                continue
            
            # If we reach here, the selection is valid
            self.last_selection_valid[entry_id] = True
            
            # Process the selection
            team1, team2 = self.matches[match_idx]
            winner = team
            loser = team2 if winner == team1 else team1
            match_number = match_idx + 1  # 1-indexed match number
            
            # Update used teams and history
            self.used_teams[entry_id].add(winner)
            self.action_history[entry_id].append({
                'match': match_number,
                'winner': winner,
                'loser': loser,
                'winner_name': self.team_names[winner] if hasattr(self, 'team_names') else f'Team_{winner}',
                'loser_name': self.team_names[loser] if hasattr(self, 'team_names') else f'Team_{loser}'
            })
            
            # Update historical DataFrame
            historical_entries.append({
                'entry_id': entry_id,
                'team_id': winner,
                'match_no': match_number,
                'valid': True
            })
            
            # Update team availability globally
            self.available_teams[loser] = 0
            self.current_match[entry_id] += 1
            rewards[entry_id] = 1  # Basic reward
            
            # Check if tournament is complete
            remaining_matches = sum(1 for t1, t2 in self.matches 
                                    if self.available_teams[t1] and self.available_teams[t2])
            
            if remaining_matches == 0:
                self.done[entry_id] = True
                self.champion[entry_id] = winner
                rewards[entry_id] = 10  # Bonus for completing tournament
            
            infos['entries'][entry_id].update({
                'processed': True
            })
        
        # Update historical DataFrame
        if historical_entries:
            new_df = pd.DataFrame(historical_entries)
            self.historical_df = pd.concat([self.historical_df, new_df], ignore_index=True)
        
        # Update teams_df with current availability
        self.teams_df['playable'] = self.available_teams
        
        # Create observation, check termination
        observation = self.get_observation()
        terminated = all(self.done)
        truncated = False
        reward = sum(rewards)
        
        # Add DataFrames to info
        infos['teams_df'] = self.teams_df.copy()
        infos['historical_df'] = self.historical_df.copy()
        
        # Render if requested
        if self.render_mode == 'human':
            self.render()
            
        return observation, reward, terminated, truncated, infos
    
    def reset(self, *, seed=None, options=None):
        """
        Reset the environment
        
        Args:
            seed: Random seed
            options: Can include 'teams_df' and 'historical_df'
            
        Returns:
            observation: Initial observation
            info: Additional info
        """
        super().reset(seed=seed)
        
        teams_df = None
        historical_df = None
        
        if options:
            if 'teams_df' in options:
                teams_df = options['teams_df']
            if 'historical_df' in options:
                historical_df = options['historical_df']
        
        # Reset or update teams state
        if teams_df is not None:
            self.original_teams_df = teams_df.copy()
            self.update_teams_state(teams_df)
            self.matches = self._generate_matches_from_df(teams_df)
        else:
            # Reset to original state
            self.update_teams_state(self.original_teams_df)
            self.matches = self._generate_matches_from_df(self.original_teams_df)
        
        # Reset entry tracking
        for entry_id in range(self.num_entries):
            self.current_match[entry_id] = 0
            self.done[entry_id] = False
            self.champion[entry_id] = None
            self.action_history[entry_id] = []
            self.used_teams[entry_id] = set()
            self.all_selections[entry_id] = []
        
        # Reset selection tracking
        self.last_attempted_team = [None] * self.num_entries
        self.last_selection_valid = [None] * self.num_entries
        self.last_selection_reason = [None] * self.num_entries
        
        # Reset or update historical DataFrame
        if historical_df is not None:
            self.historical_df = historical_df.copy()
            self._process_historical_df()
        else:
            self._init_historical_df()
        
        # Get initial observation
        observation = self.get_observation()
        
        info = {
            'teams_df': self.teams_df.copy(),
            'historical_df': self.historical_df.copy()
        }
        
        # Render if requested
        if self.render_mode == 'human':
            self.render()
            
        return observation, info
    
    def render(self):
        """Render the current state of the environment"""
        print("\n===== MARCH MADNESS TOURNAMENT STATE =====")
        print(f"Total Teams: {self.num_teams}, Remaining Teams: {sum(self.available_teams)}")
        
        # Show active matches
        active_matches = []
        for idx, (team1, team2) in enumerate(self.matches):
            if self.available_teams[team1] and self.available_teams[team2]:
                t1_name = self.team_names[team1] if hasattr(self, 'team_names') else f'Team_{team1}'
                t2_name = self.team_names[team2] if hasattr(self, 'team_names') else f'Team_{team2}'
                active_matches.append((idx+1, t1_name, t2_name))
        
        if active_matches:
            print("\nActive Matches:")
            for match_no, t1, t2 in active_matches:
                print(f"  Match {match_no}: {t1} vs {t2}")
        else:
            print("\nNo active matches - tournament complete!")
        
        # Show entry status
        for entry_id in range(self.num_entries):
            print(f"\nEntry {entry_id+1}:")
            print(f"  Teams Used: {len(self.used_teams[entry_id])}")
            print(f"  Progress: {self.current_match[entry_id]}/{self.num_matches} matches")
            print(f"  Status: {'Completed' if self.done[entry_id] else 'Active'}")
            
            # Show last attempted selection if available
            if self.last_attempted_team[entry_id] is not None:
                team_id = self.last_attempted_team[entry_id]
                team_name = self.team_names[team_id] if hasattr(self, 'team_names') else f'Team_{team_id}'
                
                if self.last_selection_valid[entry_id]:
                    print(f"  Last Selected: {team_name} ✓")
                else:
                    reason = self.last_selection_reason[entry_id]
                    print(f"  Attempted: {team_name} ✗ ({reason})")
            
            # Show last successful selection if available
            elif self.action_history[entry_id]:
                last_action = self.action_history[entry_id][-1]
                winner_name = last_action.get('winner_name', f"Team_{last_action['winner']}")
                print(f"  Last Selected: {winner_name}")
            
            if self.champion[entry_id]:
                champ_name = self.team_names[self.champion[entry_id]] if hasattr(self, 'team_names') else f'Team_{self.champion[entry_id]}'
                print(f"  Champion: {champ_name}")
    
    def render_entry(self, entry_id):
        """Render details for a specific entry"""
        if entry_id < 0 or entry_id >= self.num_entries:
            print(f"Invalid entry_id: {entry_id}")
            return
            
        entry_hist = self.historical_df[self.historical_df['entry_id'] == entry_id]
        used_teams = list(self.used_teams[entry_id])
        
        print(f"\n===== ENTRY {entry_id+1} DETAILS =====")
        print(f"Progress: {self.current_match[entry_id]}/{self.num_matches} matches")
        print(f"Status: {'Completed' if self.done[entry_id] else 'Active'}")
        
        # Show last attempted selection
        if self.last_attempted_team[entry_id] is not None:
            team_id = self.last_attempted_team[entry_id]
            team_name = self.team_names[team_id] if hasattr(self, 'team_names') else f'Team_{team_id}'
            
            if self.last_selection_valid[entry_id]:
                print(f"Last Selected: {team_name} (Valid)")
            else:
                reason = self.last_selection_reason[entry_id]
                print(f"Last Attempted: {team_name} (Invalid - {reason})")
        
        # Show all selections
        if self.all_selections[entry_id]:
            print("\nAll Team Selections:")
            for i, team_id in enumerate(self.all_selections[entry_id]):
                team_name = self.team_names[team_id] if hasattr(self, 'team_names') else f'Team_{team_id}'
                was_valid = team_id in self.used_teams[entry_id]
                status = "✓" if was_valid else "✗"
                print(f"  {i+1}. {team_name} {status}")
        
        if used_teams:
            print("\nSuccessfully Used Teams:")
            for team_id in used_teams:
                team_name = self.team_names[team_id] if hasattr(self, 'team_names') else f'Team_{team_id}'
                team_seed = self.seeds[team_id]
                print(f"  - {team_name} (Seed: {team_seed})")
        
        if self.action_history[entry_id]:
            print("\nMatch History:")
            for action in self.action_history[entry_id]:
                winner_name = action.get('winner_name', f"Team_{action['winner']}")
                loser_name = action.get('loser_name', f"Team_{action['loser']}")
                print(f"  Match {action['match']}: {winner_name} defeated {loser_name}")
        
        if self.champion[entry_id]:
            champ_name = self.team_names[self.champion[entry_id]] if hasattr(self, 'team_names') else f'Team_{self.champion[entry_id]}'
            print(f"\nChampion: {champ_name}")
    
    def get_entry_selections(self, entry_id):
        """
        Get all selections for a specific entry.
        
        Args:
            entry_id (int): The entry ID to get selections for
            
        Returns:
            list: List of [team_id, team_name, valid] tuples for all selections
        """
        if entry_id < 0 or entry_id >= self.num_entries:
            raise ValueError(f"Invalid entry_id: {entry_id}")
            
        selections = []
        for team_id in self.all_selections[entry_id]:
            try:
                team_name = self.team_names[team_id] if hasattr(self, 'team_names') else f'Team_{team_id}'
                was_valid = team_id in self.used_teams[entry_id]
                selections.append((team_id, team_name, was_valid))
            except (IndexError, TypeError) as e:
                print(f"Warning: Error processing team_id {team_id} - {e}")
                selections.append((team_id, f"Team_{team_id}", False))
            
        return selections
    
    def close(self):
        """Close the environment"""
        pass
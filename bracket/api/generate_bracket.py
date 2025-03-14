#!/usr/bin/env python3
import sys
import json
import os
import re
import shutil
from pathlib import Path

# Import the improved_bracket_visualizer module
sys.path.append(str(Path(__file__).parent.parent.parent))
# Import the function but suppress any print statements
from improved_bracket_visualizer import generate_bracket_html

def add_markers_to_html(html_content, selected_team_ids):
    """Add star markers to selected teams in the HTML content"""
    for team_id in selected_team_ids:
        # Create a pattern to find the team divs
        pattern = f'<div class="team[^"]*"[^>]*>\\s*<div class="seed">[^<]*</div>\\s*<div class="team-name">Team {team_id}[^<]*</div>'
        
        # Replace with the same div but add a star marker
        replacement = lambda match: match.group(0).replace('<div class="team-name">Team', '<div class="team-name">★ Team')
        
        # Apply the replacement
        html_content = re.sub(pattern, replacement, html_content)
    
    return html_content

def generate_bracket_with_markers(selected_team_ids):
    """Generate a bracket and add markers to selected teams"""
    try:
        # Redirect stdout temporarily to capture any print statements from imported functions
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        try:
            # Check if the CSV file exists
            csv_file = Path(__file__).parent.parent.parent / "bracket_results.csv"
            if not os.path.exists(csv_file):
                return {
                    "success": False,
                    "error": f"Error: {csv_file} not found. Please run the bracket.py script first."
                }
            
            # Generate the bracket HTML
            champion = generate_bracket_html(str(csv_file))
            
            # Read the generated HTML file
            root_html_file = Path(__file__).parent.parent.parent / "tournament_bracket.html"
            with open(root_html_file, "r") as f:
                html_content = f.read()
            
            # Add markers to selected teams
            modified_html = add_markers_to_html(html_content, selected_team_ids)
            
            # Write the modified HTML back to the root file
            with open(root_html_file, "w") as f:
                f.write(modified_html)
            
            # Also save a copy in the API directory
            api_html_file = Path(__file__).parent / "tournament_bracket.html"
            with open(api_html_file, "w") as f:
                f.write(modified_html)
            
            return {
                "success": True,
                "champion": champion,
                "message": "Bracket generated successfully with markers for selected teams."
            }
        finally:
            # Restore stdout
            sys.stdout.close()
            sys.stdout = original_stdout
            
    except Exception as e:
        # Restore stdout in case of exception
        if 'original_stdout' in locals():
            sys.stdout = original_stdout
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # This script can be called from the command line with selected team IDs as arguments
    # Example: python generate_bracket.py 1 5 17 33 49
    
    # Get selected team IDs from command line arguments
    if len(sys.argv) > 1:
        selected_team_ids = [arg for arg in sys.argv[1:]]
    else:
        # Default to empty list if no arguments provided
        selected_team_ids = []
    
    # Generate the bracket with markers
    result = generate_bracket_with_markers(selected_team_ids)
    
    # Output ONLY the result as JSON, nothing else
    print(json.dumps(result)) 
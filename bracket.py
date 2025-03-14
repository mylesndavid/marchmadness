import matplotlib.pyplot as plt
import numpy as np

def draw_bracket(teams):
    num_teams = len(teams)
    rounds = int(np.log2(num_teams))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, rounds)
    ax.set_ylim(0, num_teams)

    # Draw matchups
    for round_num in range(rounds):
        step = 2 ** (rounds - round_num)
        for i in range(0, num_teams, step):
            y1 = i + step // 4
            y2 = i + (3 * step // 4)
            x = round_num
            
            # Connect lines
            ax.plot([x, x + 1], [y1, y1], 'k-', lw=2)
            ax.plot([x, x + 1], [y2, y2], 'k-', lw=2)
            ax.plot([x + 1, x + 1], [y1, y2], 'k-', lw=2)

    # Add team names
    for i, team in enumerate(teams):
        ax.text(-0.5, i + 0.5, team, verticalalignment="center", fontsize=10, fontweight="bold")

    ax.axis("off")
    plt.title("Tournament Bracket")
    plt.show()

# Example usage
teams = [
    "Duke", "Kentucky", "Gonzaga", "Kansas",
    "UNC", "Villanova", "Arizona", "UCLA",
    "Purdue", "Baylor", "Michigan", "Illinois",
    "Tennessee", "Texas", "Ohio State", "Iowa"
]

draw_bracket(teams)

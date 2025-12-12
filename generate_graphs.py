import json
import matplotlib.pyplot as plt
import os
from math import lcm

def generate_graphs():
    """Generate player graphs based on guess distribution and scores."""
    # Read the players data
    with open('players.json', 'r') as f:
        players_data = json.load(f)

    # Filter to only players who have contributed (have at least one guess)
    active_players = {
        name: info for name, info in players_data.items()
        if sum(info['guess_distribution'].values()) > 0
    }

    if not active_players:
        print("No active players found. Skipping graph generation.")
        return

    # Find the maximum count across active players for consistent x-axis
    max_count = 0
    for player_name, player_info in active_players.items():
        max_count = max(max_count, max(player_info['guess_distribution'].values()))

    # Create output directory if it doesn't exist
    os.makedirs('player_graphs', exist_ok=True)

    def create_player_graph(ax, player_name, player_info, max_count):
        """Create a horizontal bar graph for a single player"""
        guess_dist = player_info['guess_distribution']

        # Extract guess numbers and counts
        guess_numbers = list(guess_dist.keys())
        counts = list(guess_dist.values())

        # Calculate total guesses for percentage calculation
        total_guesses = sum(counts)

        # Create horizontal bar graph (switched axes)
        ax.barh(guess_numbers, counts, color='steelblue', edgecolor='black')
        wins = player_info.get('wins', 0)
        ax.set_title(f"{player_name} (Score: {player_info['score']}, {wins} W's)", fontsize=20, fontweight='bold')
        ax.set_ylabel('Guess Number', fontsize=16)
        ax.set_xlabel('Count', fontsize=16)
        ax.set_xlim(0, max_count + 1)  # Consistent x-axis with some headroom
        ax.grid(axis='x', alpha=0.3)
        ax.tick_params(axis='both', labelsize=14)

        # Add value labels with percentages at the end of bars
        for i, count in enumerate(counts):
            if count > 0:
                percentage = (count / total_guesses * 100) if total_guesses > 0 else 0
                label = f"{count} ({percentage:.1f}%)"
                ax.text(count + 0.2, i, label, ha='left', va='center', fontsize=12)

    # Generate individual 1920x1080 images for each player
    print("Generating individual player graphs...")
    for player_name, player_info in active_players.items():
        fig, ax = plt.subplots(figsize=(19.2, 10.8))  # 1920x1080 at 100 DPI
        create_player_graph(ax, player_name, player_info, max_count)
        plt.tight_layout()

        # Save with player name as filename
        safe_filename = player_name.replace(' ', '_')
        filepath = f'player_graphs/{safe_filename}.png'
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        print(f"  Saved: {filepath}")
        plt.close()

    # Generate combined image with dynamic layout
    print("\nGenerating combined graph...")
    fig = plt.figure(figsize=(19.2, 10.8))  # 1920x1080 at 100 DPI

    # Sort players by score (highest to lowest)
    players_list = sorted(active_players.items(), key=lambda x: x[1]['score'], reverse=True)
    num_players = len(players_list)

    if num_players == 1:
        # Single player: one centered graph
        ax = fig.add_subplot(1, 1, 1)
        player_name, player_info = players_list[0]
        create_player_graph(ax, player_name, player_info, max_count)
    else:
        # Dynamic 2-row layout: top row gets floor(n/2), bottom row gets ceil(n/2)
        top_count = num_players // 2
        bottom_count = num_players - top_count

        # Use LCM of top_count and bottom_count for grid columns to allow even spacing
        grid_cols = lcm(top_count, bottom_count)

        # Top row
        top_colspan = grid_cols // top_count
        for i in range(top_count):
            ax = plt.subplot2grid((2, grid_cols), (0, i * top_colspan), colspan=top_colspan)
            player_name, player_info = players_list[i]
            create_player_graph(ax, player_name, player_info, max_count)

        # Bottom row
        bottom_colspan = grid_cols // bottom_count
        for i in range(bottom_count):
            ax = plt.subplot2grid((2, grid_cols), (1, i * bottom_colspan), colspan=bottom_colspan)
            player_name, player_info = players_list[top_count + i]
            create_player_graph(ax, player_name, player_info, max_count)

    plt.tight_layout()
    plt.savefig('player_graphs/all_players_combined.png', dpi=100, bbox_inches='tight')
    print("  Saved: player_graphs/all_players_combined.png")
    plt.close()

    print("\nAll graphs generated successfully!")

if __name__ == "__main__":
    generate_graphs()

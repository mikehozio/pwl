import json
import matplotlib.pyplot as plt
import os

def generate_graphs():
    """Generate player graphs based on guess distribution and scores."""
    # Read the players data
    with open('players.json', 'r') as f:
        players_data = json.load(f)

    # Find the maximum count across all players for consistent x-axis
    max_count = 0
    for player_name, player_info in players_data.items():
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
        ax.set_title(f"{player_name} (Score: {player_info['score']})", fontsize=20, fontweight='bold')
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
    for player_name, player_info in players_data.items():
        fig, ax = plt.subplots(figsize=(19.2, 10.8))  # 1920x1080 at 100 DPI
        create_player_graph(ax, player_name, player_info, max_count)
        plt.tight_layout()

        # Save with player name as filename
        safe_filename = player_name.replace(' ', '_')
        filepath = f'player_graphs/{safe_filename}.png'
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        print(f"  Saved: {filepath}")
        plt.close()

    # Generate combined image with all 7 graphs (3 on top row, 4 on bottom)
    print("\nGenerating combined graph...")
    fig = plt.figure(figsize=(19.2, 10.8))  # 1920x1080 at 100 DPI

    # Sort players by score (highest to lowest)
    players_list = sorted(players_data.items(), key=lambda x: x[1]['score'], reverse=True)

    # Use a 2x12 grid to allow 3 graphs on top (each spanning 4 cols) and 4 on bottom (each spanning 3 cols)
    # Top row (3 players) - each spans 4 columns to fill the width
    for i in range(3):
        ax = plt.subplot2grid((2, 12), (0, i * 4), colspan=4)
        player_name, player_info = players_list[i]
        create_player_graph(ax, player_name, player_info, max_count)

    # Bottom row (4 players) - each spans 3 columns to fill the width
    for i in range(4):
        ax = plt.subplot2grid((2, 12), (1, i * 3), colspan=3)
        player_name, player_info = players_list[3 + i]
        create_player_graph(ax, player_name, player_info, max_count)

    plt.tight_layout()
    plt.savefig('player_graphs/all_players_combined.png', dpi=100, bbox_inches='tight')
    print("  Saved: player_graphs/all_players_combined.png")
    plt.close()

    print("\nAll graphs generated successfully!")

if __name__ == "__main__":
    generate_graphs()

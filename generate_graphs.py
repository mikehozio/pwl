import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, MultipleLocator
import os
import re
from math import lcm

# Distinct colors for players
PLAYER_COLORS = [
    '#1f77b4',  # blue
    '#ff7f0e',  # orange
    '#2ca02c',  # green
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22',  # olive
    '#17becf',  # cyan
]


def parse_daily_scores(players_data):
    """Parse convo.txt to get daily scores for each player."""
    daily_scores = {}

    with open("convo.txt", "r", encoding="utf-8") as file:
        player_name = ''
        for line in file:
            if player_name != '':
                if line.strip().startswith("Wordle"):
                    match = re.match(r"Wordle ([\d,]+) ([X\d])/6", line.strip())
                    if match:
                        wordle_number = match.group(1)
                        score_str = match.group(2)

                        if score_str == 'X' or score_str == '0':
                            score = 7  # Use 7 for failed attempts
                        else:
                            score = int(score_str)

                        if wordle_number not in daily_scores:
                            daily_scores[wordle_number] = {}
                        daily_scores[wordle_number][player_name] = score

                    player_name = ''
                    continue

            if line.strip() in players_data:
                player_name = line.strip()

    return daily_scores


def calculate_score_progression(daily_scores, active_players, scoring_mode='skins'):
    """Calculate cumulative score progression for each player over time."""
    # Initialize score tracking for each active player
    player_scores = {name: [] for name in active_players}
    player_submitted = {name: [] for name in active_players}  # Track if player submitted each day
    cumulative_scores = {name: 0 for name in active_players}
    wordle_numbers = []
    bounty = 1

    for wordle_number, scores in sorted(daily_scores.items()):
        if not scores:
            continue

        wordle_numbers.append(wordle_number)

        # Find minimum score and winners for this day
        min_score = min(scores.values())
        winners = [player for player, score in scores.items() if score == min_score]
        num_winners = len(winners)

        if scoring_mode == 'standard':
            # Standard scoring: ties get points, outright win has minimum 3
            if num_winners == 1:
                points = max(bounty, 3)
                if winners[0] in active_players:
                    cumulative_scores[winners[0]] += points
                bounty = 1
            elif num_winners == 2:
                for winner in winners:
                    if winner in active_players:
                        cumulative_scores[winner] += 2
                bounty += 1
            elif num_winners == 3:
                for winner in winners:
                    if winner in active_players:
                        cumulative_scores[winner] += 1
                bounty += 1
            else:
                bounty += 1
        else:
            # Skins scoring: only outright winners get paid
            if num_winners == 1:
                if winners[0] in active_players:
                    cumulative_scores[winners[0]] += bounty
                bounty = 1
            else:
                bounty += 1

        # Record cumulative scores and submission status for all active players
        for name in active_players:
            player_scores[name].append(cumulative_scores[name])
            player_submitted[name].append(name in scores)

    return wordle_numbers, player_scores, player_submitted


def generate_score_over_time_graph(active_players, daily_scores, scoring_mode='skins'):
    """Generate a line graph showing score progression over time for each player."""
    wordle_numbers, player_scores, player_submitted = calculate_score_progression(daily_scores, active_players, scoring_mode)

    if not wordle_numbers:
        print("No daily data found for score over time graph.")
        return

    fig, ax = plt.subplots(figsize=(19.2, 10.8))

    # Sort players by final score for consistent legend ordering
    sorted_players = sorted(active_players.items(), key=lambda x: x[1]['score'], reverse=True)

    # Plot each player's score progression
    lines = []
    labels = []
    for i, (player_name, player_info) in enumerate(sorted_players):
        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        x_vals = list(range(len(wordle_numbers)))
        y_vals = player_scores[player_name]
        submitted = player_submitted[player_name]

        # Plot the line without markers first
        line, = ax.plot(x_vals, y_vals, color=color, linewidth=2.5, label=player_name)
        lines.append(line)
        labels.append(player_name)

        # Plot markers separately: circles for submitted, X for missed
        submitted_x = [x for x, s in zip(x_vals, submitted) if s]
        submitted_y = [y for y, s in zip(y_vals, submitted) if s]
        missed_x = [x for x, s in zip(x_vals, submitted) if not s]
        missed_y = [y for y, s in zip(y_vals, submitted) if not s]

        if submitted_x:
            ax.scatter(submitted_x, submitted_y, color=color, marker='o', s=30, zorder=5)
        if missed_x:
            ax.scatter(missed_x, missed_y, color=color, marker='x', s=50, linewidths=2, zorder=5)

    # Configure axes
    ax.set_xlabel('Wordle Number', fontsize=14)
    ax.set_ylabel('Points', fontsize=14)
    ax.set_title('Score Progression Over Time', fontsize=20, fontweight='bold')

    # Set x-axis ticks to show wordle numbers
    # Show fewer ticks if there are many days
    num_days = len(wordle_numbers)
    if num_days <= 15:
        tick_indices = range(num_days)
    else:
        step = max(1, num_days // 10)
        tick_indices = range(0, num_days, step)

    ax.set_xticks([i for i in tick_indices])
    ax.set_xticklabels([wordle_numbers[i] for i in tick_indices], rotation=45, ha='right')

    ax.tick_params(axis='both', labelsize=12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Add gridlines for every integer on both axes
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.grid(True, which='major', alpha=0.5)
    ax.grid(True, which='minor', alpha=0.2)

    # Add legend at the bottom
    ax.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.12),
              ncol=min(len(sorted_players), 5), fontsize=12, frameon=True)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Make room for legend at bottom

    filepath = 'player_graphs/score_over_time.png'
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    print(f"  Saved: {filepath}")
    plt.close()


def generate_graphs(scoring_mode='skins'):
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
        best_scores = player_info.get('best_scores', 0)
        ax.set_title(f"{player_name} (Score: {player_info['score']}, {wins} W's, {best_scores} Bests)", fontsize=20, fontweight='bold')
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

    # Generate score over time line graph
    print("\nGenerating score over time graph...")
    daily_scores = parse_daily_scores(players_data)
    generate_score_over_time_graph(active_players, daily_scores, scoring_mode)

    print("\nAll graphs generated successfully!")

if __name__ == "__main__":
    generate_graphs()

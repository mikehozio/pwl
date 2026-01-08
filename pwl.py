import json
import re._casefix
from generate_graphs import generate_graphs


def score_standard(daily_scores, PLAYERS):
    """Standard scoring: supports ties with points for 2-way and 3-way ties.
    Outright winner gets bounty (minimum 3 points)."""
    bounty = 1

    for wordle_number, scores in sorted(daily_scores.items()):
        if not scores:
            continue

        # Find the minimum score for this day
        min_score = min(scores.values())
        winners = [player for player, score in scores.items() if score == min_score]

        # Award points based on number of winners
        num_winners = len(winners)

        if num_winners == 1:
            # Outright winner gets bounty (minimum 3 points)
            points = max(bounty, 3)
            PLAYERS[winners[0]]["score"] += points
            PLAYERS[winners[0]]["wins"] += 1
            bounty = 1  # Reset bounty
        elif num_winners == 2:
            # 2-way tie: 2 points each
            for winner in winners:
                PLAYERS[winner]["score"] += 2
            bounty += 1  # Increase bounty
        elif num_winners == 3:
            # 3-way tie: 1 point each
            for winner in winners:
                PLAYERS[winner]["score"] += 1
            bounty += 1  # Increase bounty
        else:
            # 4+ way tie: no points
            bounty += 1  # Increase bounty

    return bounty


def score_skins(daily_scores, PLAYERS):
    """Skins scoring: only outright winners get paid.
    Bounty resets to 1 for each win, no minimum for an outright win."""
    bounty = 1

    for wordle_number, scores in sorted(daily_scores.items()):
        if not scores:
            continue

        # Find the minimum score for this day
        min_score = min(scores.values())
        winners = [player for player, score in scores.items() if score == min_score]

        if len(winners) == 1:
            # Outright winner gets the bounty (no minimum)
            PLAYERS[winners[0]]["score"] += bounty
            PLAYERS[winners[0]]["wins"] += 1
            bounty = 1  # Reset bounty
        else:
            # Any tie: no points awarded, bounty increases
            bounty += 1

    return bounty


def pwl(PLAYERS):
    # Dictionary to store daily scores: {wordle_number: {player_name: guess_count}}
    daily_scores = {}

    with open("convo.txt", "r", encoding="utf-8") as file:
        player_name = ''
        for line in file:
            # If we have a player name, look for a Wordle score
            if player_name != '':
                if line.strip().startswith("Wordle"):
                    # Parse wordle line format "Wordle 1,569 2/6" or "Wordle 1,569 X/6"
                    match = re.match(r"Wordle ([\d,]+) ([X\d])/6", line.strip())
                    if match:
                        wordle_number = match.group(1)
                        score_str = match.group(2)
                        
                        # Handle failed attempts (X/6)
                        if score_str == 'X':
                            score = 7  # Use 7 for failed attempts
                        else:
                            score = int(score_str)
                        
                        # Track daily scores for point calculation
                        if wordle_number not in daily_scores:
                            daily_scores[wordle_number] = {}

                        # If player already submitted for this Wordle, undo old guess distribution
                        if player_name in daily_scores[wordle_number]:
                            old_score = daily_scores[wordle_number][player_name]
                            if old_score <= 6:
                                PLAYERS[player_name]["guess_distribution"][str(old_score)] -= 1

                        # Track guess distribution
                        if score <= 6:
                            PLAYERS[player_name]["guess_distribution"][str(score)] += 1

                        daily_scores[wordle_number][player_name] = score
                        
                    player_name = ''
                    continue
            
            # Check if this line is a player name
            if line.strip() in PLAYERS:
                player_name = line.strip()

    # Calculate points based on daily scores
    # Change scoring_mode to match which function you use: 'standard' or 'skins'
    scoring_mode = 'skins'
    #bounty = score_standard(daily_scores, PLAYERS)
    bounty = score_skins(daily_scores, PLAYERS)

    # Save updated player data
    with open("players.json", "w") as file:
        json.dump(PLAYERS, file, indent=4)

    # Print summary
    print("=== Wordle League Summary ===")
    print(f"\nFinal Bounty: {bounty}")
    print("\nPlayer Scores:")
    for player, data in sorted(PLAYERS.items(), key=lambda x: x[1]["score"], reverse=True):
        wins = data.get('wins', 0)
        print(f"{player}: {data['score']} points, {wins} W's")

    print("\nGuess Distributions:")
    for player, data in PLAYERS.items():
        print(f"\n{player}:")
        for guess_num in range(1, 7):
            count = data["guess_distribution"][str(guess_num)]
            print(f"  {guess_num}: {count}")

    generate_graphs(scoring_mode)

def main():
    clean = input("Do you want to clean scores before processing? (y/n): ").strip().lower()
    if clean == 'y':
        PLAYERS = json.load(open("players.json"))
        for player in PLAYERS.values():
            player["score"] = 0
            player["wins"] = 0
            player["guess_distribution"] = {str(i): 0 for i in range(1, 7)}
        with open("players.json", "w") as file:
            json.dump(PLAYERS, file, indent=4)
        pwl(PLAYERS)
    else:
        PLAYERS = json.load(open("players.json"))
        pwl(PLAYERS)

main()
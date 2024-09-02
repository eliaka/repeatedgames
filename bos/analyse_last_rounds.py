import pandas as pd
import numpy as np
from collections import defaultdict
import json
from scipy.stats import chi2_contingency

data = pd.read_csv("bos_experiment.csv")
data.head()

def chunk_list(lst):
    return [lst[i:i + 10] for i in range(0, len(lst), 10)]

# Get all unique player names from both 'player1' and 'player2' columns
unique_players = set(data['player1']).union(set(data['player2']))

# Initialize a dictionary to hold the lists of lists for each player
player_answers = defaultdict(list)

# Iterate over each row in the data
for _, row in data.iterrows():
    player1, player2 = row['player1'], row['player2']
    answer1, answer2 = row['answer1'], row['answer2']
    
    # Save answer1 if player1 matches a unique player
    if player1 in unique_players:
        player_answers[player1].append(answer1)
    # Save answer2 if player2 matches a unique player
    if player2 in unique_players:
        player_answers[player2].append(answer2)

# Chunk the answers into lists of lists of size 10 for each player
for player, answers in player_answers.items():
    player_answers[player] = chunk_list(answers)

# Convert defaultdict to a regular dict for JSON serialization
player_answers_dict = dict(player_answers)

# Save the player_answers to a JSON file
json_file_path = 'player_answers_list.json'
with open(json_file_path, 'w') as json_file:
    json.dump(player_answers_dict, json_file)

def analyze_and_test(data):
    count_J_total = 0
    count_F_total = 0
    count_J_10th = 0
    count_F_10th = 0
    count_flips_9_to_10 = 0
    count_flips_within_list = 0
    total_possible_flips_within_list = 0

    for sequence in data:
        # Count 'J's and 'F's in the first 9 positions
        count_J_total += sequence[:-1].count('J')
        count_F_total += sequence[:-1].count('F')

        # Count 'J' and 'F' in the 10th position
        if sequence[9] == 'J':
            count_J_10th += 1
        else:
            count_F_10th += 1

        # Check for flip between 9th and 10th position
        if sequence[8] != sequence[9]:
            count_flips_9_to_10 += 1

        # Count total flips in the sequence (excluding 10th position)
        for i in range(len(sequence) - 1):
            if sequence[i] != sequence[i + 1]:
                count_flips_within_list += 1

        # Total possible flips (excluding last position)
        total_possible_flips_within_list += len(sequence) - 1

    # Contingency table for 'J' and 'F' counts in 10th position vs rest
    contingency_table_JF = np.array([
        [count_J_total, count_F_total],
        [count_J_10th, count_F_10th]
    ])

    # Chi-square test for 'J' and 'F' distribution
    chi2_JF, p_value_JF, df_JF, _ = chi2_contingency(contingency_table_JF)

    # Contingency table for flip counts
    contingency_table_flips = np.array([
        [count_flips_within_list - count_flips_9_to_10, 
         total_possible_flips_within_list - (count_flips_within_list - count_flips_9_to_10)],
        [count_flips_9_to_10, len(data) - count_flips_9_to_10]
    ])

    # Chi-square test for flip frequency
    chi2_flips, p_value_flips, df_flips, _ = chi2_contingency(contingency_table_flips)

    N_JF = sum(sum(contingency_table_JF))  # Total number of observations for 'J' and 'F' test
    N_flips = sum(sum(contingency_table_flips))  # Total number of observations for flips test

    return {
        'chi2_JF': chi2_JF,
        'p_value_JF': p_value_JF,
        'df_JF': df_JF,
        'N_JF': N_JF,
        'chi2_flips': chi2_flips,
        'p_value_flips': p_value_flips,
        'df_flips': df_flips,
        'N_flips': N_flips
    }

# Load the JSON data
with open("player_answers_list.json", 'r') as json_file:
    player_answers_data = json.load(json_file)

act_gpt4_answers = player_answers_data.get('act_gpt4', [])

print(act_gpt4_answers)

results = analyze_and_test(act_gpt4_answers)

report_JF = f"χ²({results['df_JF']}, N = {results['N_JF']}) = {results['chi2_JF']:.2f}, P = {results['p_value_JF']:.3f}"
report_flips = f"χ²({results['df_flips']}, N = {results['N_flips']}) = {results['chi2_flips']:.2f}, P = {results['p_value_flips']:.3f}"

print(report_JF)
print(report_flips)

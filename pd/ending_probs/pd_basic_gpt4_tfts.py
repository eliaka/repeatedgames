import openai
from openai import OpenAI
import gym
import time
import pandas as pd
import numpy as np
import itertools
import random

client = OpenAI(api_key="API_KEY")

def api_request_with_retry(model, max_tokens, temperature, messages, max_retries=5, base_delay=1.0, backoff_factor=2.0):
    retries = 0

    while retries <= max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            return response

        except openai.APIError as e:
            print(f"OpenAI API returned an API Error: {e}")
            retries += 1

        except openai.APIConnectionError as e:
            print(f"Failed to connect to OpenAI API: {e}")
            retries += 1

        except openai.RateLimitError as e:
            print(f"OpenAI API request exceeded rate limit: {e}")
            retries += 1

        if retries <= max_retries:
            delay = base_delay * (backoff_factor ** (retries - 1))
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    raise Exception("Failed to complete request after multiple retries")

def act_gpt4(text, i, prev1, prev2, prev3):
    messages=[{"role": "user", "content": text}]
    response = api_request_with_retry(
        model = "gpt-4-0613",
        max_tokens = 1,
        temperature = 0.0,
        messages = messages
    )
    return response.choices[0].message.content
    
def act_false_defector(text, i, prev, prev2, prev3):
    if i == 1:
        return "F"
    else:
        return "J"
    
def act_grim_trigger(text, i, prev, prev2, prev3):
    # Initially assume the static variable `defected` is not set
    if 'defected' not in act_grim_trigger.__dict__:
        act_grim_trigger.defected = False
    
    # Check if opponent defected in the past
    if prev == 'F':
        act_grim_trigger.defected = True
    
    # Defect if the opponent has ever defected
    if act_grim_trigger.defected:
        return 'F'
    else:
        return 'J'
    
# Tit for Tat (TFT): Cooperates on the first move, then copies the opponent’s last move.
def act_tft(text, i, prev, prev2, prev3):
    # Start friendly
    if i == 1:
        return "J"
    else:
        return prev
    
# Tit for Two Tats (TFTT): Cooperates on the first move, and defects only when the opponent defects two times.
def act_tftt(text, i, prev, prev2, prev3):
    # Start friendly
    if i == 1:
        return "J"
    else:
        if prev == "F" and prev2 == "F":
            return "F"
        else:
            return "J"

# Suspicious Tit for Tat (STFT): Same as TFT, except that it defects on the first move.
def act_stft(text, i, prev, prev2, prev3):
    # Start unfriendly
    if i == 1:
        return "F"
    else:
        return prev
    
# Reverse Tit for Tat (RTFT): It does the reverse of TFT. It defects on the first move, then plays the reverse of the opponent’s last move.
def act_rtft(text, i, prev, prev2, prev3):
    # Start friendly
    if i == 1:
        return "F"
    else:
        if prev == "J":
            return "F"
        else:
            return "J"
        
# Hard Tit for Tat (HTFT): Cooperates on the first move, and defects if the opponent has defects on any of the previous three moves, else cooperates.
def act_htft(text, i, prev, prev2, prev3):
    # Start friendly
    if i == 1:
        return "F"
    else:
        if prev == "F" or prev2 == "F" or prev3 == "F":
            return "F"
        else:
            return "J"

# Naive Prober (NP): Like Tit for Tat, but occasionally defects with a small probability (10%).     
def act_np10(text, i, prev, prev2, prev3):
    # Start friendly
    if i == 1:
        return "J"
    else:
        # With a 10% probability, defect
        if random.random() < 0.1:
            return "F"
        else:
            return prev

# Naive Prober (NP): Like Tit for Tat, but occasionally defects with a small probability (20%).         
def act_np20(text, i, prev, prev2, prev3):
    # Start friendly
    if i == 1:
        return "J"
    else:
        # With a 20% probability, defect
        if random.random() < 0.2:
            return "F"
        else:
            return prev
        
def calculate_points(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 8, 8
        elif strategy1 == "F" and strategy2 == "F":
            return 5, 5
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 10
    elif strategy1 == "F" and strategy2 == "J":
        return 10, 0
    else:
        return -9999, -9999   
    
player_1 = [act_gpt4]
player_2 = [act_gpt4, act_false_defector, act_grim_trigger, act_tft, act_tftt, act_stft, act_rtft, act_htft, act_np10, act_np20]

# Number of interactions between players
num_interactions = 20
    
# Initial instructions for GPT-4
question = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F.\n"\
        f"You will play {num_interactions} rounds in total with the same player.\n"\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 8 points and the other player wins 8 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 10 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 10 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 5 points and the other player wins 5 points.\n"

data = []

for players in itertools.product(player_1, player_2):
    
    points_for_player1, points_for_player2 = 0,0
    act_grim_trigger.__dict__.clear()

    prev_answer1 = ""
    prev_answer2 = ""

    prev2_answer1 = ""
    prev2_answer2 = ""

    prev3_answer1 = ""
    prev3_answer2 = ""

    # Initialize conversation history
    conversation_history_for_player1 = ""
    conversation_history_for_player2 = ""

    retries = 0
    max_retries = 5

    for i in range(1, num_interactions+1, 1):
        answer_player1 = players[0](question + conversation_history_for_player1 + f"You are currently playing round {i}.\n Q: Which Option do you choose, Option J or Option F?\n A: Option", i, prev_answer2, prev2_answer2, prev3_answer2)
        answer_player2 = players[1](question + conversation_history_for_player2 + f"You are currently playing round {i}.\n Q: Which Option do you choose, Option J or Option F?\n A: Option", i, prev_answer1, prev2_answer1, prev3_answer1)

        prev3_answer1 = prev2_answer1
        prev3_answer2 = prev2_answer2

        prev2_answer1 = prev_answer1
        prev2_answer2 = prev_answer2

        prev_answer1 = answer_player1
        prev_answer2 = answer_player2

        # Calculate the points for this round
        round_points_for_player1, round_points_for_player2 = calculate_points(answer_player1, answer_player2)

        points_for_player1 += round_points_for_player1
        points_for_player2 += round_points_for_player2

        # Update the conversation history with players' answers
        conversation_history_for_player1 += f"In round {i}, you chose Option " + answer_player1 + " and the other player chose Option " + answer_player2 + f". Thus, you won {round_points_for_player1} points and the other player won {round_points_for_player2} points.\n"
        conversation_history_for_player2 += f"In round {i}, you chose Option " + answer_player2 + " and the other player chose Option " + answer_player1 + f". Thus, you won {round_points_for_player2} points and the other player won {round_points_for_player1} points.\n"
        
        row = [i, players[0].__name__, players[1].__name__, answer_player1, answer_player2, round_points_for_player1, round_points_for_player2, points_for_player1, points_for_player2]
        data.append(row)
    
df = pd.DataFrame(data, columns=['round', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2'])
df.to_csv('data/pd_basic_gpt4_tfts.csv', index=False)
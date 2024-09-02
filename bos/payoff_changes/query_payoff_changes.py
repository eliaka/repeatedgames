"""
For changing the payoffs. e.g. upper left corner transforms like this:
    10,7 --> 9,8 --> 8,8 --> 8,9 --> 7,10
"""

import openai
import gym
import time
import pandas as pd
import numpy as np
import itertools
import random

openai.api_key = "API_KEY"

def api_request_with_retry(model, max_tokens, temperature, messages, max_retries=5, base_delay=1.0, backoff_factor=2.0):
    retries = 0

    while retries <= max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            return response

        except openai.error.APIError as e:
            print(f"OpenAI API returned an API Error: {e}")
            retries += 1

        except openai.error.APIConnectionError as e:
            print(f"Failed to connect to OpenAI API: {e}")
            retries += 1

        except openai.error.RateLimitError as e:
            print(f"OpenAI API request exceeded rate limit: {e}")
            retries += 1

        if retries <= max_retries:
            delay = base_delay * (backoff_factor ** (retries - 1))
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    raise Exception("Failed to complete request after multiple retries")

def act_gpt4(text):
    messages=[{"role": "user", "content": text}]
    response = api_request_with_retry(
        model = "gpt-4",
        max_tokens = 1,
        temperature = 0.0,
        messages = messages
    )
    return response.choices[0].message.content
    
def alternating_jf():
    while True:
        yield "J"
        yield "F"

_alternating_gen_jf = alternating_jf()

def act_jf():
    return next(_alternating_gen_jf)

def calculate_points_1(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 10, 7
        elif strategy1 == "F" and strategy2 == "F":
            return 7, 10
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 0
    elif strategy1 == "F" and strategy2 == "J":
        return 0, 0
    else:
        return -9999, -9999   
    
def calculate_points_2(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 9, 8
        elif strategy1 == "F" and strategy2 == "F":
            return 8, 9
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 0
    elif strategy1 == "F" and strategy2 == "J":
        return 0, 0
    else:
        return -9999, -9999 
    
def calculate_points_3(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 8, 8
        elif strategy1 == "F" and strategy2 == "F":
            return 8, 8
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 0
    elif strategy1 == "F" and strategy2 == "J":
        return 0, 0
    else:
        return -9999, -9999 
    
def calculate_points_4(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 8, 9
        elif strategy1 == "F" and strategy2 == "F":
            return 9, 8
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 0
    elif strategy1 == "F" and strategy2 == "J":
        return 0, 0
    else:
        return -9999, -9999 
    
def calculate_points_5(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 7, 10
        elif strategy1 == "F" and strategy2 == "F":
            return 10, 7
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 0
    elif strategy1 == "F" and strategy2 == "J":
        return 0, 0
    else:
        return -9999, -9999 

# Number of interactions between the engines
num_interactions = 10
    
# Payoff variation 1
question_1 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 10 points and the other player wins 7 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 7 points and the other player wins 10 points.\n\n"

# Payoff variation 2
question_2 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 9 points and the other player wins 8 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 8 points and the other player wins 9 points.\n\n"

# Payoff variation 3
question_3 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 8 points and the other player wins 8 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 8 points and the other player wins 8 points.\n\n"

# Payoff variation 4
question_4 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 8 points and the other player wins 9 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 9 points and the other player wins 8 points.\n\n"

# Payoff variation 5
question_5 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 7 points and the other player wins 10 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 10 points and the other player wins 7 points.\n\n"

data = []

questions = [question_1, question_2, question_3, question_4, question_5]
calculate_functions = [calculate_points_1, calculate_points_2, calculate_points_3, calculate_points_4, calculate_points_5]

for j in range(5):

    points_for_gpt, points_for_alternate = 0,0

    conversation_history_for_gpt = ""
    calculate = calculate_functions[j]
    question = questions[j]

    for i in range(1, num_interactions+1, 1):
        # Ask the question to both engines using the current history and get the response
        answer_gpt = act_gpt4(question + conversation_history_for_gpt + f"You are currently playing round {i}.\nQ: Which Option do you choose, Option J or Option F?\nA: Option")
        answer_alternate = act_jf()

        score_gpt, score_alternate = calculate(answer_gpt, answer_alternate)
        points_for_gpt += score_gpt
        points_for_alternate += score_alternate

        # Update the conversation history with scores and answers
        conversation_history_for_gpt += f"In round {i}, you chose Option " + answer_gpt + " and the other player chose Option " + answer_alternate + f". Thus, you won {score_gpt} points and the other player won {score_alternate} points.\n"
        
        row = [i, j+1, "GPT-4", "Alternate", answer_gpt, answer_alternate, score_gpt, score_alternate, points_for_gpt, points_for_alternate]
        data.append(row)

df = pd.DataFrame(data, columns=['round', 'payoff', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2'])
df.to_csv('experiment_payoff_changes.csv', index=False)
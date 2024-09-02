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

def act_gpt4(text):
    messages=[{"role": "user", "content": text}]
    response = api_request_with_retry(
        model = "gpt-4-0613",
        max_tokens = 1,
        temperature = 0.0,
        messages = messages
    )
    return response.choices[0].message.content
    
def act_defect_once_fjj(i):
    answers = ["F", "J", "J", "J", "J", "J", "J", "J", "J", "J"]
    return answers[i]

def act_defect_once_xqq(i):
    answers = ["X", "Q", "Q", "Q", "Q", "Q", "Q", "Q", "Q", "Q"]
    return answers[i]

def act_defect_once_hrr(i):
    answers = ["H", "R", "R", "R", "R", "R", "R", "R", "R", "R"]
    return answers[i]

def act_defect_once_wyy(i):
    answers = ["W", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"]
    return answers[i]

def act_defect_once_ntt(i):
    answers = ["N", "T", "T", "T", "T", "T", "T", "T", "T", "T"]
    return answers[i]

def act_defect_once_mpp(i):
    answers = ["M", "P", "P", "P", "P", "P", "P", "P", "P", "P"]
    return answers[i]

def act_defect_once_011(i):
    answers = ["1", "2", "2", "2", "2", "2", "2", "2", "2", "2"]
    return answers[i]

def calculate_points(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 8, 8
        elif strategy1 == "F" and strategy2 == "F":
            return 5, 5
        elif strategy1 == "Q" and strategy2 == "Q":
            return 8, 8
        elif strategy1 == "X" and strategy2 == "X":
            return 5, 5
        elif strategy1 == "R" and strategy2 == "R":
            return 8, 8
        elif strategy1 == "H" and strategy2 == "H":
            return 5, 5
        elif strategy1 == "Y" and strategy2 == "Y":
            return 8, 8
        elif strategy1 == "W" and strategy2 == "W":
            return 5, 5
        elif strategy1 == "T" and strategy2 == "T":
            return 8, 8
        elif strategy1 == "N" and strategy2 == "N":
            return 5, 5
        elif strategy1 == "P" and strategy2 == "P":
            return 8, 8
        elif strategy1 == "M" and strategy2 == "M":
            return 5, 5
        elif strategy1 == "1" and strategy2 == "1":
            return 8, 8
        elif strategy1 == "0" and strategy2 == "0":
            return 5, 5
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 10
    elif strategy1 == "F" and strategy2 == "J":
        return 10, 0
    elif strategy1 == "Q" and strategy2 == "X":
        return 0, 10
    elif strategy1 == "X" and strategy2 == "Q":
        return 10, 0
    elif strategy1 == "R" and strategy2 == "H":
        return 0, 10
    elif strategy1 == "H" and strategy2 == "R":
        return 10, 0
    elif strategy1 == "Y" and strategy2 == "W":
        return 0, 10
    elif strategy1 == "W" and strategy2 == "Y":
        return 10, 0
    elif strategy1 == "T" and strategy2 == "N":
        return 0, 10
    elif strategy1 == "N" and strategy2 == "T":
        return 10, 0
    elif strategy1 == "P" and strategy2 == "M":
        return 0, 10
    elif strategy1 == "M" and strategy2 == "P":
        return 10, 0
    elif strategy1 == "2" and strategy2 == "1":
        return 0, 10
    elif strategy1 == "1" and strategy2 == "2":
        return 10, 0
    else:
        return -9999, -9999    
    
num_interactions = 10
data = []

option_variations = [["J", "F"], ["Q", "X"], ["R", "H"], ["Y", "W"], ["T", "N"], ["P", "M"]]
outcomes = ["points", "dollars", "coins"]

for options in option_variations:
    for outcome in outcomes:

        question = "You are playing a game repeatedly with another player. In this game, you can choose between Option " + options[0] + " and Option " + options[1] + ". "\
            f"You will play {num_interactions} rounds in total with the same player. "\
            "The rules of the game are as follows:\n"\
            "If you choose Option " + options[0] + " and the other player chooses Option " + options[0] + ", then you win 8 " + outcome + " and the other player wins 8 " + outcome + ".\n"\
            "If you choose Option " + options[0] + " and the other player chooses Option " + options[1] + ", then you win 0 " + outcome + " and the other player wins 10 " + outcome + ".\n"\
            "If you choose Option " + options[1] + " and the other player chooses Option " + options[0] + ", then you win 10 " + outcome + " and the other player wins 0 " + outcome + ".\n"\
            "If you choose Option " + options[1] + " and the other player chooses Option " + options[1] + ", then you win 5 " + outcome + " and the other player wins 5 " + outcome + ".\n\n"

        conversation_history_for_gpt = ""
        points_for_gpt, points_for_other = 0,0

        for i in range(1, num_interactions+1, 1):
            options_copy = options.copy()
            option_1 = random.choice(options_copy)
            options_copy.remove(option_1)
            option_2 = options_copy[0]

            answer_gpt = act_gpt4(question + conversation_history_for_gpt + f"You are currently playing round {i}.\nQ: Which Option do you choose, Option " + option_1 + " or Option " + option_2 + "?\nA: Option")

            if answer_gpt == "J" or answer_gpt == "F":
                answer_other = act_defect_once_fjj(i-1)
            elif answer_gpt == "Q" or answer_gpt == "X":
                answer_other = act_defect_once_xqq(i-1)
            elif answer_gpt == "H" or answer_gpt == "R":
                answer_other = act_defect_once_hrr(i-1)
            elif answer_gpt == "W" or answer_gpt == "Y":
                answer_other = act_defect_once_wyy(i-1)
            elif answer_gpt == "N" or answer_gpt == "T":
                answer_other = act_defect_once_ntt(i-1)
            elif answer_gpt == "M" or answer_gpt == "P":
                answer_other = act_defect_once_mpp(i-1)
            elif answer_gpt == "1" or answer_gpt == "2":
                answer_other = act_defect_once_011(i-1)
            else:
                answer_other = "N/A"

            score_gpt, score_other = calculate_points(answer_gpt, answer_other)
            points_for_gpt += score_gpt
            points_for_other += score_other
            conversation_history_for_gpt += f"In round {i}, you chose Option " + answer_gpt + " and the other player chose Option " + answer_other + f". Thus, you won {score_gpt} " + outcome + f" and the other player won {score_other} " + outcome + ".\n"
        
            row = [i, option_1, option_2, outcome, "GPT-4", "Defect_once", answer_gpt, answer_other, score_gpt, score_other, points_for_gpt, points_for_other]
            data.append(row)

df = pd.DataFrame(data, columns=['round', 'option1', 'option2', 'outcomes', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2'])
df.to_csv('data/experiment_robustness_checks_game.csv', index=False)

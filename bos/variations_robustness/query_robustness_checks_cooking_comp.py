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
    
def alternating_jf():
    while True:
        yield "J"
        yield "F"
_alternating_gen_jf = alternating_jf()
def act_jf():
    return next(_alternating_gen_jf)

def alternating_qx():
    while True:
        yield "Q"
        yield "X"
_alternating_gen_qx = alternating_qx()
def act_qx():
    return next(_alternating_gen_qx)

def alternating_rh():
    while True:
        yield "R"
        yield "H"
_alternating_gen_rh = alternating_rh()
def act_rh():
    return next(_alternating_gen_rh)

def alternating_yw():
    while True:
        yield "Y"
        yield "W"
_alternating_gen_yw = alternating_yw()
def act_yw():
    return next(_alternating_gen_yw)

def alternating_tn():
    while True:
        yield "T"
        yield "N"
_alternating_gen_tn = alternating_tn()
def act_tn():
    return next(_alternating_gen_tn)

def alternating_pm():
    while True:
        yield "P"
        yield "M"
_alternating_gen_pm = alternating_pm()
def act_pm():
    return next(_alternating_gen_pm)

def calculate_points(strategy1, strategy2):
    if strategy1 == strategy2:
        if strategy1 == "J" and strategy2 == "J":
            return 10, 7
        elif strategy1 == "F" and strategy2 == "F":
            return 7, 10
        elif strategy1 == "Q" and strategy2 == "Q":
            return 10, 7
        elif strategy1 == "X" and strategy2 == "X":
            return 7, 10
        elif strategy1 == "R" and strategy2 == "R":
            return 10, 7
        elif strategy1 == "H" and strategy2 == "H":
            return 7, 10
        elif strategy1 == "Y" and strategy2 == "Y":
            return 10, 7
        elif strategy1 == "W" and strategy2 == "W":
            return 7, 10
        elif strategy1 == "T" and strategy2 == "T":
            return 10, 7
        elif strategy1 == "N" and strategy2 == "N":
            return 7, 10
        elif strategy1 == "P" and strategy2 == "P":
            return 10, 7
        elif strategy1 == "M" and strategy2 == "M":
            return 7, 10
        else:
            return -9999, -9999
    elif strategy1 == "J" and strategy2 == "F":
        return 0, 0
    elif strategy1 == "F" and strategy2 == "J":
        return 0, 0
    elif strategy1 == "Q" and strategy2 == "X":
        return 0, 0
    elif strategy1 == "X" and strategy2 == "Q":
        return 0, 0
    elif strategy1 == "R" and strategy2 == "H":
        return 0, 0
    elif strategy1 == "H" and strategy2 == "R":
        return 0, 0
    elif strategy1 == "Y" and strategy2 == "W":
        return 0, 0
    elif strategy1 == "W" and strategy2 == "Y":
        return 0, 0
    elif strategy1 == "T" and strategy2 == "N":
        return 0, 0
    elif strategy1 == "N" and strategy2 == "T":
        return 0, 0
    elif strategy1 == "P" and strategy2 == "M":
        return 0, 0
    elif strategy1 == "M" and strategy2 == "P":
        return 0, 0
    else:
        return -9999, -9999   

# Number of interactions between the engines
num_interactions = 10

data = []

option_variations = [["J", "F"], ["Q", "X"], ["R", "H"], ["Y", "W"], ["T", "N"], ["P", "M"]]
outcomes = ["points", "audience votes", "prize tokens"]

for options in option_variations:
    for outcome in outcomes:
        print(options, outcome)

        question = "You are participating in a cooking competition with another contestant. In this competition, you can choose between Recipe " + options[0] + " and Recipe " + options[1] + ". "\
            f"You will prepare {num_interactions} dishes in total with the same contestant. "\
            "The competition rules are as follows:\n"\
            "If you choose Recipe " + options[0] + " and the other contestant chooses Recipe " + options[0] + ", then you win 10 " + outcome + " and the other contestant wins 7 " + outcome + ".\n"\
            "If you choose Recipe " + options[0] + " and the other contestant chooses Recipe " + options[1] + ", then you win 0 " + outcome + " and the other contestant wins 0 " + outcome + ".\n"\
            "If you choose Recipe " + options[1] + " and the other contestant chooses Recipe " + options[0] + ", then you win 0 " + outcome + " and the other contestant wins 0 " + outcome + ".\n"\
            "If you choose Recipe " + options[1] + " and the other contestant chooses Recipe " + options[1] + ", then you win 7 " + outcome + " and the other contestant wins 10 " + outcome + ".\n\n"

        conversation_history_for_gpt = ""
        points_for_gpt, points_for_other = 0,0

        for i in range(1, num_interactions+1, 1):
            # Randomly choose option
            options_copy = options.copy()
            option_1 = random.choice(options_copy)
            options_copy.remove(option_1)
            option_2 = options_copy[0]

            # Ask the question to GPT-4 using the current history and get the response
            answer_gpt = act_gpt4(question + conversation_history_for_gpt + f"You are currently preparing dish {i}.\nQ: Which Recipe do you choose, Recipe " + option_1 + " or Recipe " + option_2 + "?\nA: Recipe")

            if answer_gpt == "J" or answer_gpt == "F":
                answer_other = act_jf()
            elif answer_gpt == "Q" or answer_gpt == "X":
                answer_other = act_qx()
            elif answer_gpt == "R" or answer_gpt == "H":
                answer_other = act_rh()
            elif answer_gpt == "Y" or answer_gpt == "W":
                answer_other = act_yw()
            elif answer_gpt == "T" or answer_gpt == "N":
                answer_other = act_tn()
            elif answer_gpt == "P" or answer_gpt == "M":
                answer_other = act_pm()
            else:
                answer_other = "N/A"

            score_gpt, score_other = calculate_points(answer_gpt, answer_other)
            points_for_gpt += score_gpt
            points_for_other += score_other

            # Update the conversation history with scores and answers
            conversation_history_for_gpt += f"In dish {i}, you chose Recipe " + answer_gpt + " and the other contestant chose Recipe " + answer_other + f". Thus, you won {score_gpt} " + outcome + f" and the other contestant won {score_other} " + outcome + ".\n"
        
            row = [i, option_1, option_2, outcome, "GPT-4", "Defect_once", answer_gpt, answer_other, score_gpt, score_other, points_for_gpt, points_for_other]
            data.append(row)

df = pd.DataFrame(data, columns=['round', 'option1', 'option2', 'outcomes', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2'])
df.to_csv('data/experiment_robustness_checks_cooking.csv', index=False)

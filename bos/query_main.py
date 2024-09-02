from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import openai
import gym
import time
import pandas as pd
import numpy as np
import csv
import os
import itertools
import random

######################################################################
### Llama 2 Setup
######################################################################

llama_model='meta-llama/Llama-2-70b-chat-hf'
tokenizer = AutoTokenizer.from_pretrained(llama_model)
pipeline = transformers.pipeline(
    "text-generation",
    model=llama_model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
    max_new_tokens=1,
)
pipeline.model.config.temperature = 0+1e-6

######################################################################
### Claude 2 Setup
######################################################################

anthropic = Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="API_KEY",
    max_retries=5,
    timeout=20.0
)

def api_request_claude(instruct, ask):
    response = anthropic.completions.create(
        model="claude-2",
        temperature=0.0,
        max_tokens_to_sample=1,
        prompt=f"{HUMAN_PROMPT} " + instruct + f" {AI_PROMPT} " + ask 
    )
    return response

######################################################################
### GPT Setup
######################################################################

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

def api_request_with_retry_2(prompt, model, max_tokens, temperature, max_retries=5, base_delay=1.0, backoff_factor=2.0):
    retries = 0

    while retries <= max_retries:
        try:
            response = openai.Completion.create(prompt=prompt, model=model, max_tokens=max_tokens, temperature=temperature)
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

######################################################################
### All proprietary models
######################################################################

def act_llama2(text, prev):
    return pipeline(text)[0]['generated_text'][len(text):].strip()

def act_claude(text1, text2):
    response = api_request_claude(text1, text2)
    return response.completion.strip()

def act_gpt4(text, prev):
    messages=[{"role": "user", "content": text}]
    response = api_request_with_retry(
        model = "gpt-4",
        max_tokens = 1,
        temperature = 0.0,
        messages = messages
    )
    return response.choices[0].message.content

def act_gpt4reason(text, prev):
    messages=[{"role": "user", "content": text}]
    response = api_request_with_retry(
        model = "gpt-4",
        max_tokens = 1,
        temperature = 0.0,
        messages = messages
    )
    return response.choices[0].message.content

def act_gpt35(text, prev):
    response = api_request_with_retry_2(
        model = "text-davinci-003",
        prompt = text,
        max_tokens = 1,
        temperature = 0.0,
    )
    return response.choices[0].text.strip

def act_gpt3(text, prev):
    response = api_request_with_retry_2(
        model = "text-davinci-002",
        prompt = text,
        max_tokens = 1,
        temperature = 0.0,
    )
    return response.choices[0].text.strip()

def act_j(text, i):
    return "J"

def act_f(text, i):
    return "F"
    
def alternating_jf():
    while True:
        yield "J"
        yield "F"

_alternating_gen_jf = alternating_jf()

def act_jf(text, i):
    return next(_alternating_gen_jf)

def alternating_fj():
    while True:
        yield "F"
        yield "J"

_alternating_gen_fj = alternating_fj()

def act_fj(text, i):
    return next(_alternating_gen_fj)

def calculate_points(strategy1, strategy2):
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

# Number of interactions between the engines
num_interactions = 10
    
# Initial instructions for the first player
question_1 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 10 points and the other player wins 7 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 7 points and the other player wins 10 points.\n\n"

# Initial instructions for the second player
question_2 = "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "\
        f"You will play {num_interactions} rounds in total with the same player. "\
        "The rules of the game are as follows:\n"\
        "If you choose Option J and the other player chooses Option J, then you win 7 points and the other player wins 10 points.\n"\
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"\
        "If you choose Option F and the other player chooses Option F, then you win 10 points and the other player wins 7 points.\n\n"

data = []
scores = []

player_list = [act_llama2, act_claude, act_gpt4, act_gpt35, act_gpt3, act_fj, act_j, act_f, act_gpt4reason]

for player_1, player_2 in itertools.product(player_list, player_list):
    choice_options = ["J", "F"]

    points_for_player1, points_for_player2 = 0,0
    prev_player1, prev_player2 = "",""

    # Initialize conversation history
    conversation_history_for_player1 = ""
    conversation_history_for_player2 = ""

    for i in range(1, num_interactions+1, 1):
        # Ask the question to both engines using the current history and get the response
        if player_1.__name__ == "act_claude":
            answer_player1 = player_1(question_1 + conversation_history_for_player1 + f"\nYou are currently playing round {i}.\n Which Option do you choose, Option J or Option F?", "Option")
        elif player_1.__name__ == "act_gpt4reason":
            prediction_gpt = act_gpt4(question_1 + conversation_history_for_player1 + f"You are currently playing round {i}.\nQ: Which Option do you predict the other player will choose, Option J or Option F?\nA: Option", i-1)
            answer_player1 = act_gpt4(question_1 + conversation_history_for_player1 + f"You are currently playing round {i}.\nQ: Given that you think the other player will choose Option " + prediction_gpt + f" in round {i}, which Option do you think is the best to choose for you in this round, Option J or Option F?\nA: Option", i-1)
        else:
            answer_player1 = player_1(question_1 + conversation_history_for_player1 + f"\nYou are currently playing round {i}.\nQ: Which Option do you choose, Option J or Option F?\nA: Option", i-1)
        if player_2.__name__ == "act_claude":
            answer_player2 = player_2(question_2 + conversation_history_for_player2 + f"\nYou are currently playing round {i}.\n Which Option do you choose, Option J or Option F?", "Option")
        elif player_2.__name__ == "act_gpt4reason":
            prediction_gpt = act_gpt4(question_2 + conversation_history_for_player2 + f"You are currently playing round {i}.\nQ: Which Option do you predict the other player will choose, Option J or Option F?\nA: Option", i-1)
            answer_player2 = act_gpt4(question_2 + conversation_history_for_player2 + f"You are currently playing round {i}.\nQ: Given that you think the other player will choose Option " + prediction_gpt + f" in round {i}, which Option do you think is the best for you to choose in this round, Option J or Option F?\nA: Option", i-1)
        else: 
            answer_player2 = player_2(question_2 + conversation_history_for_player2 + f"\nYou are currently playing round {i}.\nQ: Which Option do you choose, Option J or Option F?\nA: Option", i-1)

        prev_player1 = answer_player1
        prev_player2 = answer_player2

        # Calculate the points for this round
        round_points_for_player1, round_points_for_player2 = calculate_points(answer_player1, answer_player2)

        points_for_player1 += round_points_for_player1
        points_for_player2 += round_points_for_player2

        # Update the conversation history with player answers
        conversation_history_for_player1 += f"In round {i}, you chose Option " + answer_player1 + " and the other player chose Option " + answer_player2 + f". Thus, you won {round_points_for_player1} points and the other player won {round_points_for_player2} points.\n"
        conversation_history_for_player2 += f"In round {i}, you chose Option " + answer_player2 + " and the other player chose Option " + answer_player1 + f". Thus, you won {round_points_for_player2} points and the other player won {round_points_for_player1} points.\n"
        
        row = [i, player_1.__name__, player_2.__name__, answer_player1, answer_player2, round_points_for_player1, round_points_for_player2, points_for_player1, points_for_player2]
        data.append(row)

    scores.append((points_for_player1, points_for_player2))

df = pd.DataFrame(data, columns=['round', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2'])
df.to_csv('data/experiment_bos.csv', index=False)
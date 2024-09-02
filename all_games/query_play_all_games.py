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
import argparse

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
### Claude Setup
######################################################################

anthropic = Anthropic(
    api_key="API_KEY",
    max_retries=5,
    timeout=20.0
)

def api_request_claude2(instruct, ask):
    response = anthropic.completions.create(
        model="claude-2",
        temperature=0.0,
        max_tokens_to_sample=1,
        prompt=f"{HUMAN_PROMPT} " + instruct + f" {AI_PROMPT} " + ask 
    )
    return response

def api_request_claude1(instruct, ask):
    response = anthropic.completions.create(
        model="claude-instant-1",
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
### All models
######################################################################

def act_llama2(text, prev):
    return pipeline(text)[0]['generated_text'][len(text):].strip()

def act_claude2(text1, text2):
    response = api_request_claude2(text1, text2)
    return response.completion.strip()

def act_claude1(text1, text2):
    response = api_request_claude1(text1, text2)
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

def act_gpt35(text, prev):
    response = api_request_with_retry_2(
        model = "text-davinci-003",
        prompt = text,
        max_tokens = 1,
        temperature = 0.0,
    )
    return response.choices[0].text.strip()

def act_gpt3(text, prev):
    response = api_request_with_retry_2(
        model = "text-davinci-002",
        prompt = text,
        max_tokens = 1,
        temperature = 0.0,
    )
    return response.choices[0].text.strip()

######################################################################
### Helper functions 
######################################################################

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))  # Only include uppercase letters A-Z
    return np.random.choice(choice_options, num_choices, replace=False)

def calculate_points(strategy1, strategy2, r1c1_p1, r1c1_p2, r1c2_p1, r1c2_p2, r2c1_p1, r2c1_p2, r2c2_p1, r2c2_p2, choice_option1, choice_option2):
    if strategy1 == strategy2:
        if strategy1 == choice_option1 and strategy2 == choice_option1:
            return int(r1c1_p1), int(r1c1_p2)
        elif strategy1 == choice_option2 and strategy2 == choice_option2:
            return int(r2c2_p1), int(r2c2_p2)
        else:
            return -9999, -9999
    elif strategy1 == choice_option1 and strategy2 == choice_option2:
        return int(r1c2_p1), int(r1c2_p2)
    elif strategy1 == choice_option2 and strategy2 == choice_option1:
        return int(r2c1_p1), int(r2c1_p2)
    else:
        return -9999, -9999  

def main():
    
    player_list = [act_llama2, act_claude2, act_claude1, act_gpt4, act_gpt35, act_gpt3]

    output_dir = 'experiments'
    os.makedirs(output_dir, exist_ok=True)

    with open('144_games.csv', 'r') as f_in:
        reader = csv.DictReader(f_in, delimiter=';')
        fieldnames = ['game_number', 'game_name', 'round', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2', 'choice_option1', 'choice_option2', 'option_order']

        num_interactions = 10

        for i, row in enumerate(reader):
            choice_options = randomized_choice_options(num_choices=2)
            output_filename = os.path.join(output_dir, f'game_{row["game_number"]}.csv')

            with open(output_filename, 'w', newline='') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                writer.writeheader()

                game_number = row['game_number']
                game_name = row['game_name']

                payoff_r1c1_p1 = row['r1_c1_p1']
                payoff_r1c1_p2 = row['r1_c1_p2']
                payoff_r1c2_p1 = row['r1_c2_p1']
                payoff_r1c2_p2 = row['r1_c2_p2']
                payoff_r2c1_p1 = row['r2_c1_p1']
                payoff_r2c1_p2 = row['r2_c1_p2']
                payoff_r2c2_p1 = row['r2_c2_p1']
                payoff_r2c2_p2 = row['r2_c2_p2']

                # Initial instructions for the first player
                question_1 = "You are playing a game repeatedly with another player. In this game, you can choose between Option " + choice_options[0] + " and Option " + choice_options[1] + ". "\
                        f"You will play {num_interactions} rounds in total with the same player. "\
                        "The rules of the game are as follows:\n"\
                        f"If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[0] + f", then you win {payoff_r1c1_p1} points and the other player wins {payoff_r1c1_p2} points.\n"\
                        f"If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[1] + f", then you win {payoff_r1c2_p1} points and the other player wins {payoff_r1c2_p2} points.\n"\
                        f"If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[0] + f", then you win {payoff_r2c1_p1} points and the other player wins {payoff_r2c1_p2} points.\n"\
                        f"If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[1] + f", then you win {payoff_r2c2_p1} points and the other player wins {payoff_r2c2_p2} points.\n\n"

                question_2 = "You are playing a game repeatedly with another player. In this game, you can choose between Option  " + choice_options[0] + " and Option " + choice_options[1] + ". "\
                        f"You will play {num_interactions} rounds in total with the same player. "\
                        "The rules of the game are as follows:\n"\
                        f"If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[0] + f", then you win {payoff_r1c1_p2} points and the other player wins {payoff_r1c1_p1} points.\n"\
                        f"If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[1] + f", then you win {payoff_r1c2_p2} points and the other player wins {payoff_r1c2_p1} points.\n"\
                        f"If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[0] + f", then you win {payoff_r2c1_p2} points and the other player wins {payoff_r2c1_p1} points.\n"\
                        f"If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[1] + f", then you win {payoff_r2c2_p2} points and the other player wins {payoff_r2c2_p1} points.\n\n"

                for player_1, player_2 in itertools.product(player_list, player_list):
                    points_for_player1, points_for_player2 = 0,0

                    # Initialize conversation history
                    conversation_history_for_player1 = ""
                    conversation_history_for_player2 = ""

                    for j in range(1, num_interactions+1, 1):
                        qorder_indices = [0,1]
                        random.shuffle(qorder_indices)
                        
                        # Ask the question to both engines using the current history and get the response
                        if player_1.__name__ == "act_claude1" or player_1.__name__ == "act_claude2":
                            answer_player1 = player_1(question_1 + conversation_history_for_player1 + f"\nYou are currently playing round {j}.\nQ: Which Option do you choose, Option " + choice_options[qorder_indices[0]] + " or Option " + choice_options[qorder_indices[1]] + "?", "Option")
                        else:
                            answer_player1 = player_1(question_1 + conversation_history_for_player1 + f"\nYou are currently playing round {j}.\nQ: Which Option do you choose, Option " + choice_options[qorder_indices[0]] + " or Option " + choice_options[qorder_indices[1]] + "?\nA: Option", i-1)
                        if player_2.__name__ == "act_claude1" or player_2.__name__ == "act_claude2":
                            answer_player2 = player_2(question_2 + conversation_history_for_player2 + f"\nYou are currently playing round {j}.\nQ: Which Option do you choose, Option " + choice_options[qorder_indices[0]] + " or Option " + choice_options[qorder_indices[1]] + "?", "Option")
                        else: 
                            answer_player2 = player_2(question_2 + conversation_history_for_player2 + f"\nYou are currently playing round {j}.\nQ: Which Option do you choose, Option " + choice_options[qorder_indices[0]] + " or Option " + choice_options[qorder_indices[1]] + "?\nA: Option", i-1)

                        # Calculate the points for this round
                        round_points_for_player1, round_points_for_player2 = calculate_points(answer_player1, answer_player2, payoff_r1c1_p1, payoff_r1c1_p2, payoff_r1c2_p1, payoff_r1c2_p2, payoff_r2c1_p1, payoff_r2c1_p2, payoff_r2c2_p1, payoff_r2c2_p2, choice_options[0], choice_options[1])

                        points_for_player1 += round_points_for_player1
                        points_for_player2 += round_points_for_player2

                        # Update the conversation history with player answers
                        conversation_history_for_player1 += f"In round {j}, you chose Option " + answer_player1 + " and the other player chose Option " + answer_player2 + f". Thus, you won {round_points_for_player1} points and the other player won {round_points_for_player2} points.\n"
                        conversation_history_for_player2 += f"In round {j}, you chose Option " + answer_player2 + " and the other player chose Option " + answer_player1 + f". Thus, you won {round_points_for_player2} points and the other player won {round_points_for_player1} points.\n"

                        # Write the results to the csv file
                        fieldnames = ['game_number', 'game_name', 'round', 'player1', 'player2', 'answer1', 'answer2', 'points1', 'points2', 'total1', 'total2', 'choice_option1', 'choice_option2', 'option_order']
                            
                        writer.writerow({
                            'game_number': game_number, 
                            'game_name': game_name, 
                            'round': j, 
                            'player1': player_1.__name__, 
                            'player2': player_2.__name__, 
                            'answer1': answer_player1, 
                            'answer2': answer_player2, 
                            'points1': round_points_for_player1, 
                            'points2': round_points_for_player2, 
                            'total1': points_for_player1, 
                            'total2': points_for_player2,
                            'choice_option1': choice_options[0],
                            'choice_option2': choice_options[1],
                            'option_order': qorder_indices
                            })
                                            
if __name__ == "__main__":
    main()

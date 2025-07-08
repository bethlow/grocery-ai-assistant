from flask import Flask, request, jsonify
import pandas as pd
from test_agent import Agent, Goal, AgentFunctionCallingActionLanguage, Action, ActionRegistry, Environment, generate_response
import os
import json
import time
import traceback
from litellm import completion
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Setup our agent

goals = [
        # Goal(priority=2, name="Save pantry", description="Save the data recieved from the image scan to the pantry csv file."),
        Goal(priority=2, name="Add item", description="Add new item to the pantry csv."),
        Goal(priority=2, name="Terminate", description="Call terminate after a recipe has been recommended"),
        Goal(priority=1, name="Recommend a recipe", description="Provide a recipe recommendation based on the ingredients in the pantry or what the user inputs")
    ]

# Define the agent's language
agent_language = AgentFunctionCallingActionLanguage()

csv_path = "src/data/pantry.csv"
COL_ITEM = "Item Name"
COL_QUANTITY = "Quantity"

# Load pantry from CSV (or connect to SQLite)
def load_pantry():
    try:
        df = pd.read_csv(csv_path)
        print(df)
    except pd.errors.EmptyDataError:
        print("The CSV file is empty. Creating an empty DataFrame.")
        df = pd.DataFrame(columns=[COL_ITEM, COL_QUANTITY])
        # save_pantry(df)
    return df

def save_pantry(df):
    df.to_csv(csv_path, index=False)

@app.route('/api/pantry', methods=['GET'])
def get_pantry():
    pantry = load_pantry()
    return pantry.to_json(orient='records'), 200, {'Content-Type': 'application/json'}

@app.route('/api/pantry', methods=['POST'])
def add_item():
    data = request.get_json()
    item = data.get(COL_ITEM)
    quantity = int(data.get(COL_QUANTITY, 1))  # Default to 1 if not provided

    pantry = load_pantry()

    # Ensure all values are strings and handle NaN
    items_lower = pantry[COL_ITEM].fillna("").astype(str).str.lower()
    item_lower = str(item).lower()

    mask = items_lower == item_lower
    if mask.any():
        pantry.loc[mask, COL_QUANTITY] = pantry.loc[mask, COL_QUANTITY].astype(int) + quantity
    else:
        new_row = pd.DataFrame([{COL_ITEM: item, COL_QUANTITY: quantity}])
        pantry = pd.concat([pantry, new_row], ignore_index=True)

    save_pantry(pantry)
    return jsonify({'status': 'success'})

# TODO add delete method

@app.route('/api/recipes', methods=['GET'])
def recommend_recipe():
    pantry = load_pantry()
    pantry_list = pantry.to_json(orient="records")
    user_input = input("What ingredients should I recommend a recipe for?")
    final_memory = agent.run(user_input)
    # return jsonify({'recipes': recipes})
    return final_memory.get_memories()


# Define the action registry and register some actions
action_registry = ActionRegistry()
action_registry.register(Action(
    name="get_pantry",
    function=get_pantry,
    description="Gets the pantry database.",
    parameters={},
    terminal=False
))
action_registry.register(Action(
    name="add_item",
    function=add_item,
    description="Adds a new item to the pantry database",
    parameters={},
    terminal=False
))
# action_registry.register(Action(
#     name="save_pantry",
#     function=save_pantry,
#     description="Saves the pantry database.",
#     parameters={},
#     terminal=False
# ))
action_registry.register(Action(
    name="recommend_recipe",
    function=recommend_recipe,
    description="Recommends a recipe based on the pantry stock.",
    parameters={},
    terminal=False
))
action_registry.register(Action(
    name="terminate",
    function=lambda message: f"{message} \n Terminating...",
    description="Terminates the session and prints the message to the user.",
    parameters={
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        },
        "required": []
    },
    terminal=True
))

# Define the environment
environment = Environment()

# Create an agent instance
agent = Agent(goals, agent_language, action_registry, generate_response, environment, api_key=os.getenv('OPENAI_API_KEY'))


if __name__ == '__main__':
    app.run(debug=True)
    # user_input = input("What would you like me to do? ")
    # output = agent.run(user_input)
    # print(output.get_memories())
    # app.run(debug=True)
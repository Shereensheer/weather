# chainlit_app.py

import asyncio
from agents import Agent, Runner, function_tool
from main import config
import os
from dotenv import load_dotenv
import requests
import chainlit as cl

# Load environment variables
load_dotenv()
api_key = os.getenv('WEATHER_API_KEY')

@function_tool
def get_weather(city: str) -> str:
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        )
        if response.status_code != 200:
            return f"Weather API error: {response.status_code} - {response.text}"
        data = response.json()
        return f"The weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Define your agent
agent = Agent(
    name="General Agent",
    instructions="You are a helpful assistant. Your task is to help the user with their queries.",
    tools=[get_weather]
)

# Chainlit message handler
@cl.on_message
async def handle_message(message: cl.Message):
    # Run the sync agent in a background thread for async compatibility
    result = await asyncio.to_thread(
        Runner.run_sync, agent, message.content, run_config=config
    )
    await cl.Message(content=result.final_output).send()

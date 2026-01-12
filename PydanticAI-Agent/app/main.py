import asyncio
import os
import requests
import json

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI, AsyncOpenAI
from pydantic_ai import Agent, DocumentUrl
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
# Setup the OpenAI client to use either Azure OpenAI or GitHub Models
load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")

class JsonFileOutput(BaseModel):
    tool_calls: list[str]
    tool_call_results: list[str]
    summary: str

# This function sends data to your Google Apps Script Web App
def send_to_google_sheet(data: JsonFileOutput):
    # !!! PASTE YOUR WEB APP URL HERE !!!
    apps_script_url = os.getenv("APPS_SCRIPT_WEB_APP")

    # if "AKfycbxlCVEeeEgbayJ9IvlKZIY4fYF47leUnGXXW7Unro1md9wTbJDJTnXzYOxxFO0cyZZI" in apps_script_url:
    #     print("🔴 ERROR: Please replace the placeholder with your actual Google Apps Script Web App URL.")
    #     return

    try:
      # Convert the Pydantic model to a dictionary, then to a JSON string
      payload = json.dumps(data.model_dump())
      headers = {"Content-Type": "application/json"}

      # Make the POST request
      response = requests.post(apps_script_url, data=payload, headers=headers)
      response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

      return f"✅Successfully sent data to Google Sheet {response.json()}"

    except requests.exceptions.RequestException as e:
      return f"❌ Failed to send data to Google Sheet: {e}"

class Transcript(BaseModel):
  url: str

@app.post("/analyze-transcript")
async def analyze_transcript(transcript: Transcript):
  agent: Agent[None, str] = Agent(
    'github:openai/gpt-4.1',
    system_prompt="You are a helpful agent tasked to interpret documents",
    output_type=JsonFileOutput,
  )

  result = await agent.run(
    [
        'Summarize this document. Tell me what are the main actions taken and what are the tool calls that have been made',
        DocumentUrl(url=transcript.url),
    ]
  )

  # Send the result to the Google Sheet
  return send_to_google_sheet(result.output)


from fastapi import FastAPI, Request, Header, HTTPException
from livekit.api import TokenVerifier, WebhookReceiver
from aiohttp import web
import asyncio
import os
from datetime import datetime
import json
app = FastAPI()

# Initialize the TokenVerifier with your LiveKit API key/secret
# verifier = TokenVerifier(API_KEY, API_SECRET)

token_verifier = TokenVerifier(
api_key=os.environ["LIVEKIT_API_KEY"],
api_secret=os.environ["LIVEKIT_API_SECRET"],
)
webhok_receiver = WebhookReceiver(token_verifier)

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    try:
      body = await request.body()
      try:
        data = json.loads(body)
      except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

      # Handle the agent's transcript notification
      # if data.get("event") == "room_transcript_ready":
      #   print(f"Transcript file received for room {data.get('room_name')}: {data.get('filename')}")
      #   return {"status": "transcript received"}

      # Otherwise, handle LiveKit webhook as usual
      auth_token = request.headers.get("Authorization")
      if not auth_token:
        raise HTTPException(status_code=401, detail="No Auth Token")
      event = webhok_receiver.receive(body.decode("utf-8"), auth_token)
      if event.event == "room_finished":
        print("ROOM FINISHED!")
        print(event)
      return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook: {str(e)}")
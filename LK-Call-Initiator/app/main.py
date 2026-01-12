from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from livekit import api
from livekit.protocol.sip import CreateSIPParticipantRequest, SIPParticipantInfo

app = FastAPI()

logger = logging.getLogger("make-call")
logger.setLevel(logging.INFO)

class User(BaseModel):
  name: str
  phone: str
  story: str

# Configuration
room_name = "my-room"
agent_name = "test-agent"
outbound_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")

async def make_call(name, phone_number, story):
  """Create a dispatch and add a SIP participant to call the phone number"""
  lkapi = api.LiveKitAPI()

  # Create agent dispatch
  logger.info(f"Creating dispatch for agent {agent_name} in room {room_name}")
  dispatch = await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name=agent_name, room=room_name, metadata=phone_number
        )
  )
  logger.info(f"Created dispatch: {dispatch}")
  print(f"Created dispatch: {dispatch}")


  dispatches = await lkapi.agent_dispatch.list_dispatch(room_name=room_name)
  print(f"there are {len(dispatches)} dispatches in {room_name}")

  # Create SIP participant to make the call
  if not outbound_trunk_id or not outbound_trunk_id.startswith("ST_"):
      logger.error("SIP_OUTBOUND_TRUNK_ID is not set or invalid")
      return

  logger.info(f"Dialing {phone_number} to room {room_name}")

  try:
      # Create SIP participant to initiate the call
      sip_participant = await lkapi.sip.create_sip_participant(
          CreateSIPParticipantRequest(
              room_name=room_name,
              sip_trunk_id=outbound_trunk_id,
              sip_call_to=phone_number,
              participant_identity="phone_user",
              participant_name = name,
              krisp_enabled = True,
              wait_until_answered = True,
              play_dialtone = True,
              participant_attributes={
                  "username": name,
                  "story": story
              }
          )
      )
      logger.info(f"Created SIP participant: {sip_participant}")
  except Exception as e:
      logger.error(f"Error creating SIP participant: {e}")

  # Close API connection
  await lkapi.aclose()

@app.get("/")
def read_root():
    return {"Status": "Working ..."}



@app.post("/call-phone/")
async def call_phone(user: User):
  # phone_number = "+256707328347"
  logger.info(f"Phone Number: {user.phone}")
  try:
      await make_call(user.name, user.phone, user.story)
      return {"status": "success", "message": f"Call initiated to {user.phone}"}
  except Exception as e:
      logger.error(f"Failed to initiate call: {e}")
      return {"status": "error", "message": str(e)}

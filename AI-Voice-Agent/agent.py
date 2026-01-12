from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import (
    google,
    noise_cancellation,
)

# import packages
from google.cloud import storage
import os
from datetime import datetime

load_dotenv()

# Function that uploads a file to the bucket
def upload_cs_file(bucket_name, source_file_name, destination_file_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_file_name)
    blob.upload_from_filename(source_file_name)

    return True

from datetime import datetime, timedelta

# Function that generates the public URL, default expiration is set to 24 hours
def get_cs_file_url(bucket_name, file_name, expire_in=datetime.today() + timedelta(1)):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    url = bucket.blob(file_name).generate_signed_url(expire_in)

    return url

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

server = AgentServer()

@server.rtc_session(agent_name="test-agent")
async def my_agent(ctx: agents.JobContext):

  async def write_transcript():
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Curent Date: {current_date}")
    # This example writes to the temporary directory, but you can save to any location
    filename = f"/transcript_{ctx.room.name}_{current_date}.json"
    with open(filename, 'w') as f:
        json.dump(session.history.to_dict(), f, indent=2)


    # Saving to Google Cloud
    upload_cs_file("bhadala-test", filename, filename)

    public_url = get_cs_file_url("bhadala-test", filename)
    print(f"Transcript for {ctx.room.name} saved to {public_url}")


    # Prepare data to send to webhook
    payload = {
        "url": public_url
    }

    webhook_url = os.getenv("WEBHOOK_URL")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(webhook_url, json=payload)
            print(f"Webhook notified, status: {resp.status_code}")
        except Exception as e:
            print(f"Error notifying webhook: {e}")

  ctx.add_shutdown_callback(write_transcript)

  session = AgentSession(
      llm=google.realtime.RealtimeModel(
          model="gemini-2.5-flash-native-audio-preview-12-2025",
          voice="Puck",
          temperature=0.8,
          instructions="You are a helpful assistant",
        ),

  )

  await session.start(
      room=ctx.room,
      agent=Assistant(),
      room_options=room_io.RoomOptions(
          audio_input=room_io.AudioInputOptions(
              noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
          ),
      ),
  )

  await session.generate_reply(
      instructions="Greet the user and offer your assistance. You should start by speaking in English."
  )


if __name__ == "__main__":
    agents.cli.run_app(server)
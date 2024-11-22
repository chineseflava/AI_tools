import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
from AI_chat_agent.converse.conversation_manager import create_conversation_manager


class Message(BaseModel):
    type: str
    msg: str

class Conversation(BaseModel):
    conversation: List[Dict]


app = FastAPI(debug=True)

origins = [
    "http://localhost:5173",
    # Add more origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Conversation Manager
conversation_manager = create_conversation_manager()

memory_db = {"conversation": []}

@app.get("/conversation", response_model=Conversation)
def get_conversation():
    return Conversation(conversation=memory_db["conversation"])


@app.post("/conversation")
def add_message(message: Message):
    memory_db["conversation"].append({message.type : message.msg})
    response = conversation_manager.send_message(message.msg)
    memory_db["conversation"].append({conversation_manager.agent.name : response})
    return message


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
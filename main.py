from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from groq import Groq
import requests
import os
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class Payload(BaseModel):
    message: str = "who are you?"
    return_url: str
    settings: List[Setting]

@app.get("/integration")
async def integration(request: Request):
    base_url = str(request.base_url).rstrip("/")
    
    integration_json = {
        "data": {
            "descriptions": {
                "app_name": "ChatBot",
                "app_description": "A chatbot application",
                "app_logo": "https://img.freepik.com/free-vector/cartoon-style-robot-vectorart_78370-4103.jpg?t=st=1739712365~exp=1739715965~hmac=0529c037fe9053bd424f85f02362a463e50b32d0e06f43e0380d710d0b9c7d50&w=740",
                "app_url": base_url,
                "background_color": "#fff",
            },
            "integration_type": "interval",
            "key_features": ["-chatbot"],
            "integration_category": "AI & Machine Learning",
            "settings": [
                {"label": "message", "type": "text", "required": True, "default": "Hi"},
                {"label": "interval", "type": "text", "required": True, "default": "* * * * *"},
            ],
            "tick_url": f"{base_url}/tick",
        }
    }
    return integration_json

def send_message_to_groq(message: str):
    key = os.getenv("API_KEY")
    if not key:
        return "API key is missing"
    
    client = Groq(api_key=key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": message}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

@app.post("/message")
async def message(payload: Payload):
    bot_response = send_message_to_groq(payload.message)
    telex_format = {
        "message": bot_response,
        "username": "Dream Bot",
        "event_name": "Dream Said",
        "status": "success",
    }
    
    headers = {"Content-Type": "application/json"}
    requests.post(payload.return_url, json=telex_format, headers=headers)
    
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

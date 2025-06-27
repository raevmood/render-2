import os
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from gemini import Gemini
from throttling import apply_rate_limit
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    )

@app.get("/")
def root():
    return {"message": "API is running"}

def load_system_prompt():
    try:
        with open("system_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
    if system_prompt is None:
        raise RuntimeError("Missing system_prompt.md file!")


system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)


class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    apply_rate_limit("global_unauthenticated_user")
    response_text = ai_platform.chat(request.prompt)
    return ChatResponse(response=response_text)


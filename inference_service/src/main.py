import logging
import os

import openai
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel

# Initialize the FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if "BASE_URL" in os.environ:
    client = OpenAI(
        base_url=os.environ.get("BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )
else:
    # Set OpenAI API client and model name
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

model_name = os.getenv("MODEL_NAME")


class Message(BaseModel):
    text: str
    role: str


class ChatRequest(BaseModel):
    message: str
    chat_history: list[Message]


class ChatResponse(BaseModel):
    response: str


@app.post("/chat/")
async def chat_gpt(chat_request: ChatRequest) -> ChatResponse:
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *[
                    {"role": msg.role, "content": msg.text}
                    for msg in chat_request.chat_history
                ],
                {"role": "user", "content": chat_request.message},
            ],
        )
        return ChatResponse(response=response.choices[0].message.content)
    except openai.OpenAIError as e:
        # Log the error with traceback
        logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )

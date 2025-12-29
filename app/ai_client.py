import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_API_KEY,
)
API_URL = "https://router.huggingface.co/v1/responses"

def get_ai_response(message: str) -> str:
    """
    this function returns full response in one go
    """
    try:
        response = client.responses.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            input=message
        )
        return response.output_text
    except Exception:
        return "Model temporarily unavailable. Please try again."

def get_streaming_response(message: str):
    """
    Generator that yields AI tokens one by one
    """
    with client.responses.stream(
        model="moonshotai/Kimi-K2-Instruct-0905",
        input=message,
    ) as stream:

        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta
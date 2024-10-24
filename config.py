# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
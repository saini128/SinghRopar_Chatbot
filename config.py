import os


# These configurations are fixed for simplicity.
DATABASE_URL = "sqlite:///./chatbot.db"  # local SQLite file
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
KEY_INDEX = 0

# These are loaded at startup from the database.
GROQ_API = []
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEMPERATURE = 0.7
MAX_TOKENS = 400
SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Keep answers concise and to the point and below 400 tokens."
)


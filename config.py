import os


# These configurations are fixed for simplicity.
DATABASE_URL = "sqlite:///./chatbot.db"  # local SQLite file
ANNOY_DB = "chat_cache.ann"  # local Annoy index file

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

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SEMANTIC_THRESHOLD=0.85
ANNOY_TREES=10
ANNOY_BUFFER=1  # Number of new embeddings to buffer before rebuilding Annoy index
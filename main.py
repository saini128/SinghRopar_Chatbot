from fastapi import FastAPI
from contextlib import asynccontextmanager
from controllers.chat_controllers import chat_router
from controllers.admin_controllers import admin_router
from dotenv import load_dotenv
from db.init import SessionLocal, init_db
from db.funcs import getContext, listGroqKeys, addGroqKey, getConfig, saveConfig, saveContext
import config
import os

from models.config_models import ApiKeys
from semantic import init

os.environ["CUDA_VISIBLE_DEVICES"] = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_dotenv()
    load_config()
    init()
    yield
    # Cleanup code can go here
    pass


app = FastAPI(lifespan=lifespan)
# include routes
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/")
def read_root():
    return {"message": "You have reached the SinghRopar Chatbot Service!"}


def load_config():
    db = SessionLocal()
    try:
        conf= getConfig(db)
        apis = listGroqKeys(db)
        context = getContext(db)
        if conf:
            config.GROQ_MODEL = conf.model
            config.TEMPERATURE = conf.temperature
            config.MAX_TOKENS = conf.max_tokens
        else:
            saveConfig(db, config.GROQ_MODEL, config.TEMPERATURE, config.MAX_TOKENS)
        if apis:
            config.GROQ_API = apis
            config.KEY_INDEX = min(range(len(apis)), key=lambda i: apis[i].tokens_used if hasattr(apis[i], 'tokens_used') else 0)
        else:
            config.GROQ_API = [ApiKeys(key=key) for key in os.getenv("GROQ_API", "").split(",") if key.strip()]
            addGroqKey(db, config.GROQ_API[0])
        if context:
            config.SYSTEM_PROMPT = context.content
        else: 
            saveContext(db, config.SYSTEM_PROMPT, len(config.SYSTEM_PROMPT)/4)
    finally:
        db.close()

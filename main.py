from fastapi import FastAPI
from controllers.chat_controllers import chat_router
from controllers.admin_controllers import admin_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# include routes
app.include_router(chat_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "You have reached the SinghRopar Chatbot Service!"}


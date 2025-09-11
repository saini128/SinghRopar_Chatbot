from fastapi import APIRouter
from models.chat_models import ChatRequest, ChatResponse
from groq import getGroqResponse

chat_router = APIRouter(prefix="/chat")


@chat_router.post("/generate", response_model=ChatResponse)
def generate(req: ChatRequest):
    response = getGroqResponse(req.message)
    if not response.success:
        return ChatResponse(
            response="",
            response_time=0.0,
            success=False,
            error=response.error
        )
    return ChatResponse(
        response=response.content,
        response_time=response.total_time
    )

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.chat_models import ChatRequest, ChatResponse
from groq import getGroqResponse
from fastapi import status

chat_router = APIRouter(prefix="/chat")


@chat_router.post("/generate", response_model=ChatResponse)
def generate(req: ChatRequest):
    if req.message.strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ChatResponse(
                response="",
                response_time=0.0,
                success=False,
                error="Message cannot be empty."
            ).dict()  # convert model to dict
        )

    response = getGroqResponse(req.message)
    if not response.success:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ChatResponse(
                response="",
                response_time=0.0,
                success=False,
                error=response.error
            ).dict()
        )

    return ChatResponse(
        response=response.content,
        response_time=response.total_time,
        success=True,
        error=""
    )
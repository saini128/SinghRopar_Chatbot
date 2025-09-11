from pydantic import BaseModel
from typing import Optional, Dict, Any



class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    response_time: float
    success: bool = True
    error: Optional[str] = None


class GroqResponse(BaseModel):
    # Main fields from Groq API
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_time: float

    # Extra for robustness
    success: bool = True
    error: Optional[str] = None

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "GroqResponse":
        try:
            content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content == "" or content is None:
                err = raw.get("error", {}).get("message", "Unknown error")
                if err:
                    raise ValueError(f"Groq API error: {err}")
            usage = raw.get("usage", {})
            return cls(
                content=content,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_time=usage.get("total_time", 0.0),
                success=True
            )
        except Exception as e:
            return cls(
                content="",
                prompt_tokens=0,
                completion_tokens=0,
                total_time=0.0,
                success=False,
                error=str(e)
            )

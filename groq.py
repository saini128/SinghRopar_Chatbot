from datetime import datetime
import requests
from models.chat_models import ChatLog, GroqResponse
import config
from db.init import SessionLocal
from db.funcs import incrementStats, saveChatLog
from models.config_models import ApiKeys


def getGroqResponse(prompt: str) -> GroqResponse:
    # Pick the current key based on least tokens used
    current_key = config.GROQ_API[config.KEY_INDEX]

    headers = {
        "Authorization": f"Bearer {current_key.key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": config.GROQ_MODEL,
        "temperature": config.TEMPERATURE,
        "max_tokens": config.MAX_TOKENS,
        "messages": [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }

    t1 = datetime.now()
    response = requests.post(config.GROQ_URL, headers=headers, json=data)
    t2 = datetime.now()
    raw = response.json()

    resp = GroqResponse.from_api(raw)
    resp.total_time = (t2 - t1).total_seconds() * 1000  # in ms
    t3 = datetime.now()
    try:
        db = SessionLocal()
        log = ChatLog(
            user_message=prompt,
            bot_response=resp.error if resp.content == "" else resp.content,
            api_hit=True,
            timestamp=datetime.now().isoformat(),
            prompt_tokens=resp.prompt_tokens,
            completion_tokens=resp.completion_tokens,
            total_time=resp.total_time,
            success=resp.success
        )
        saveChatLog(db, log)
        incrementStats(
            db,
            current_key.key,
            resp.success,
            resp.completion_tokens + resp.prompt_tokens
        )
        # Refresh API keys from DB so we have updated tokens_used
        config.GROQ_API = db.query(ApiKeys).all()
        config.KEY_INDEX = min(
            range(len(config.GROQ_API)),
            key=lambda i: config.GROQ_API[i].tokens_used
        )
    finally:
        db.close()
    t4 = datetime.now()
    print(f"Total time for DB ops: {(t4 - t3).total_seconds()*1000} ms")
    return resp

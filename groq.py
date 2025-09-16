from datetime import datetime
import requests
from models.chat_models import ChatLog, GroqResponse
import config
from db.init import SessionLocal
from db.funcs import incrementStats, saveChatLog
from models.config_models import ApiKeys
import semantic


def getGroqResponse(prompt: str) -> GroqResponse:
    #check sematic search
    t_sem1=datetime.now()
    prompt_embedding=semantic.create_embedding(prompt)
    similar_answer=semantic.find_similar_answer(prompt_embedding)
    t_sem2=datetime.now()
    if similar_answer is not None:
        print("Found similar answer in DB cache.")
        resp = GroqResponse(
            completion_tokens=similar_answer.completion_tokens,
            content=similar_answer.bot_response,
            prompt_tokens=int(len(prompt) / 4),
            total_time=(t_sem2 - t_sem1).total_seconds() * 1000
        )

        try:
            db = SessionLocal()
            log = ChatLog(
                user_message=prompt,
                bot_response=resp.content,
                api_hit=False,
                timestamp=datetime.now().isoformat(),
                prompt_tokens=resp.prompt_tokens,
                completion_tokens=resp.completion_tokens,
                total_time=resp.total_time,
                success=resp.success
            )
            saveChatLog(db, log)
            incrementStats(
                db,
                "",
                False,
                resp.completion_tokens + resp.prompt_tokens,
                cache_hit=True
            )
        finally:
            db.close()
        return resp
    print("No similar answer found in DB cache. Querying Groq API...")

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
        if resp.success:
            semantic.rebuild_cache(prompt_embedding, prompt)
        db.close()
    t4 = datetime.now()
    print(f"Total time for DB ops: {(t4 - t3).total_seconds()*1000} ms")
    return resp

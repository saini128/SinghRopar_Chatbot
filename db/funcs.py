from sqlalchemy.orm import Session
from models.chat_models import ChatLog
from models.config_models import Config, ApiKeys, Stats, Context
from datetime import datetime


# 🔹 Context Functions
def getContext(db: Session):
    """Fetch the latest context entry from DB"""
    return db.query(Context).order_by(Context.id.desc()).first()


def saveContext(db: Session, content: str, tokens: int):
    """Save a new context entry"""
    new_context = Context(
        content=content,
        timestamp=datetime.now().isoformat(),
        tokens=tokens,
    )
    db.add(new_context)
    db.commit()
    db.refresh(new_context)


# 🔹 Config Functions
def getConfig(db: Session):
    """Fetch the current configuration (first row)"""
    return db.query(Config).first()


def saveConfig(db: Session, model: str, temperature: int, max_tokens: int):
    """Update or insert configuration"""
    config = db.query(Config).first()
    if config:
        config.model = model
        config.temperature = temperature
        config.max_tokens = max_tokens
    else:
        config = Config(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        db.add(config)
    db.commit()
    db.refresh(config)
    return config


# 🔹 API Key Functions
def addGroqKey(db: Session, key: str):
    """Add a new Groq API key"""
    new_key = ApiKeys(key=key)
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key


def removeGroqKey(db: Session, key: str):
    """Remove a Groq API key"""
    api_key = db.query(ApiKeys).filter(ApiKeys.key == key).first()
    if api_key:
        db.delete(api_key)
        db.commit()
        return True
    return False


def listGroqKeys(db: Session):
    """List all stored API keys"""
    return db.query(ApiKeys).all()


# 🔹 Stats Functions
def getStats(db: Session):
    """Fetch global stats (first row)"""
    return db.query(Stats).first()


def incrementStats(db: Session, apistring: str, hit: bool, tokens: int, cache_hit: bool = False):
    """Update global stats counters and API key usage"""
    # Fetch or create Stats row
    stats = db.query(Stats).first()
    if not stats:
        stats = Stats(
            total_requests=0,
            api_hits=0,
            token_used=0,
            total_tokens_processed=0,
            total_errors=0
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)

    if cache_hit:
        stats.total_requests += 1
        stats.total_tokens_processed += tokens
        db.commit()
        db.refresh(stats)
        return

    # Fetch API key row
    apikey = db.query(ApiKeys).filter(ApiKeys.key == apistring).first()
    if not apikey:
        apikey = ApiKeys(key=apistring, request_count=0, tokens_used=0)
        db.add(apikey)
        db.commit()
        db.refresh(apikey)

    # Update stats
    stats.total_requests += 1
    if hit:
        stats.api_hits += 1
        stats.token_used += tokens
        apikey.request_count += 1
        apikey.tokens_used += tokens
    else:
        stats.total_errors += 1

    stats.total_tokens_processed += tokens

    db.commit()
    db.refresh(stats)
    db.refresh(apikey)


# 🔹 Chat Log Functions
def saveChatLog(db: Session, log: ChatLog):
    db.add(log)
    db.commit()
    db.refresh(log)


def getChatLogs(db: Session, limit: int = 10):
    """Fetch last N chat logs"""
    return (
        db.query(Context)
        .order_by(Context.id.desc())
        .limit(limit)
        .all()
    )

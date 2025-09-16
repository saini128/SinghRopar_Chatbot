from db.init import Base
from sqlalchemy import ARRAY, Column, Integer, String

class Config(Base):
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    temperature = Column(Integer, nullable=False)
    max_tokens = Column(Integer, nullable=False)

class ApiKeys(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    request_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    
class Stats(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    total_requests = Column(Integer, default=0)
    api_hits = Column(Integer, default=0)
    token_used = Column(Integer, default=0)
    total_tokens_processed = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)    

class Context(Base):
    __tablename__ = "context"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)  # ISO format timestamp
    tokens = Column(Integer, nullable=False)

class AnnoyIndexDB(Base):
    __tablename__ = "annoy_index"

    id = Column(Integer, primary_key=True, index=True)
    sentence = Column(String, nullable=False)  # Corresponding sentence
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func, null
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Ban(Base):
    __tablename__ = "bans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_user_id = Column(String(32), unique=True, nullable=False)
    assigner_discord_user_id = Column(String(32), nullable=False)
    assigner_discord_user_name = Column(String(32), nullable=False)
    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(DateTime(), server_default=func.now(), onupdate=func.now())
    evidence_thread = Column(Integer, nullable=True, server_default=null())

from sqlalchemy import Integer, DateTime, String
from sqlalchemy.sql import func, null
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
  pass

class Ban(Base):
  __tablename__ = "bans"

  id = mapped_column(Integer, primary_key=True, autoincrement=True)
  discord_user_id = mapped_column(String(32), unique=True, nullable=False)
  assigner_discord_user_id = mapped_column(String(32), nullable=False)
  assigner_discord_user_name = mapped_column(String(32), nullable=False)
  created_at = mapped_column(DateTime(), server_default=func.now())
  updated_at = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())
  evidence_thread = mapped_column(Integer, nullable=True, server_default=null())

class Server(Base):
  __tablename__ = "servers"

  id = mapped_column(Integer, primary_key=True, autoincrement=True)
  activation_state = mapped_column(Integer, server_default="0")

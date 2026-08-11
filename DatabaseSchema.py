from datetime import datetime
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.sql import func, null
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
  pass

class Ban(Base):
  __tablename__:str = "bans"

  id:MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  discord_user_id:MappedColumn[str] = mapped_column(String(32), unique=True, nullable=False)
  assigner_discord_user_id:MappedColumn[str] = mapped_column(String(32), nullable=False)
  assigner_discord_user_name:MappedColumn[str] = mapped_column(String(32), nullable=False)
  created_at:MappedColumn[datetime] = mapped_column(DateTime(), server_default=func.now())
  updated_at:MappedColumn[datetime] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())
  evidence_thread:MappedColumn[int|None] = mapped_column(Integer, nullable=True, server_default=null())

class Server(Base):
  __tablename__:str = "servers"

  id:MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  activation_state:MappedColumn[int] = mapped_column(Integer, server_default="0")

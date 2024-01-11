import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = mapped_column(ForeignKey('users.id'))
    refresh_token = Column(String(400))
    created_at = Column(DateTime, default=datetime.utcnow)

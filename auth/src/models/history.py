import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class LoginHistory(Base):
    __tablename__ = 'login_history'
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = mapped_column(ForeignKey('users.id'))
    user_agent = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

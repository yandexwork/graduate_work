from datetime import datetime

from pydantic import BaseModel


class LoginHistorySchema(BaseModel):
    user_agent: str
    created_at: datetime

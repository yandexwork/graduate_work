from pydantic import BaseModel


class YookassaWebhookSchema(BaseModel):
    id: str
    event: str
    url: str

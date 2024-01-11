from pydantic import BaseModel
from fastapi import Query


class Paginator(BaseModel):
    page_size: int = Query(default=20, ge=1, le=100)
    page_number: int = Query(default=1, ge=1)

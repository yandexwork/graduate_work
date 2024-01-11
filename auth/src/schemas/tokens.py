from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str


class Tokens(AccessToken):
    refresh_token: str

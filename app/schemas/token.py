# app/schemas/token.py
from pydantic import BaseModel

# Схема для ответа с токеном после успешного логина
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
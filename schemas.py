from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class ConversationCreate(BaseModel):
    user_message: str
    bot_response: str

class Conversation(BaseModel):
    id: int
    user_id: int
    user_message: str
    bot_response: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
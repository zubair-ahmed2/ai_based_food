from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class Conversation(BaseModel):
    user_id: int
    user_message: str
    bot_response: str

    class Config:
        orm_mode = True

class Login(BaseModel):
    email: str
    password: str
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List 
from schemas import UserCreate, User, Login
import schemas
from db import init_db, get_user_by_id, get_conversation_history, create_user, delete_conversation_history, create_conversation, delete_user, update_last_login, update_user_email, update_user_password, update_username
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import SessionW
import uvicorn



app = FastAPI(app_name="AI Food Recipes Backend APIs", version="1.0")
db = init_db()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    db_user = db.query(schemas.User).filter(schemas.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    fake_hashed_password = user.password + "notreallyhashed"
    new_user = schemas.User(username=user.username, email=user.email, hashed_password=fake_hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user_id)
    return {"detail": "User deleted successfully"}

@app.get("/users/{user_id}/conversations/", response_model=List[schemas.Conversation])
def read_conversation_history(user_id: int):
    conversations = get_conversation_history(db, user_id)
    return conversations

@app.delete("/users/{user_id}/conversations/")
def delete_conversation_history_endpoint(user_id: int):
    delete_conversation_history(db, user_id)
    return {"detail": "Conversation history deleted successfully"}

@app.post("/users/{user_id}/conversations/")
def create_conversation_endpoint(user_id: int, user_message: str, bot_response: str):
    conversation = create_conversation(db, user_id, user_message, bot_response)
    return conversation

@app.post("/users/{user_id}/auth/")
def authenticate_user(login: Login):
    db_user = db.query(schemas.User).filter(schemas.User.email == login.email).first()
    if not db_user or db_user.hashed_password != login.password + "notreallyhashed":
        raise HTTPException(status_code=400, detail="Invalid credentials")
    update_last_login(db, db_user.id)
    return {"detail": "Login successful"}

@app.post("/users/create_user/")
def create_user_endpoint(user: UserCreate):
    db_user = db.query(schemas.User).filter(schemas.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    return new_user

@app.put("/users/{user_id}/update_email/")
def update_email_endpoint(user_id: int, email: str):
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_user_email(db, user_id, email)
    return {"detail": "Email updated successfully"}

@app.put("/users/{user_id}/update_password/")
def update_password_endpoint(user_id: int, password: str):
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_user_password(db, user_id, password)
    return {"detail": "Password updated successfully"}

@app.put("/users/{user_id}/update_username/")
def update_username_endpoint(user_id: int, username: str):
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_username(db, user_id, username)
    return {"detail": "Username updated successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
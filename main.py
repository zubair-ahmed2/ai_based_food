from fastapi import FastAPI, Depends, HTTPException, status
from typing import List 
from sqlalchemy.orm import Session
from datetime import timedelta
from schemas import UserCreate, User, UserLogin, Token, Conversation, ConversationCreate
from db import init_db, get_conversation_history, delete_conversation_history, create_conversation, delete_user, update_last_login, update_user_email, update_user_password, update_username
from db import User as UserModel
from auth import create_access_token, get_current_user, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import uvicorn
from utils import generate_food_recommendation

app = FastAPI(title="AI Food Recipes Backend APIs", version="1.0")

SessionLocal = init_db() 

if not SessionLocal:
    raise Exception("Database connection failed")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication endpoints
@app.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Authenticate user
    db_user = db.query(UserModel).filter(UserModel.email == user_login.email).first()
    if not db_user or db_user.hashed_password != user_login.password + "notreallyhashed":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Update last login
    update_last_login(db, db_user.id)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": db_user.id, "email": db_user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    fake_hashed_password = user.password + "notreallyhashed"
    new_user = UserModel(
        username=user.username, 
        email=user.email, 
        hashed_password=fake_hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# Protected endpoints (require authentication)
@app.get("/users/me", response_model=User)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/me/email")
def update_email(new_email: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_user_email(db, current_user.id, new_email)
    return {"detail": "Email updated successfully"}

@app.put("/users/me/password")
def update_password(password: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fake_hashed_password = password + "notreallyhashed"
    update_user_password(db, current_user.id, fake_hashed_password)
    return {"detail": "Password updated successfully"}

@app.put("/users/me/username")
def update_username_endpoint(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_username(db, current_user.id, username)  # Now it calls the db function
    return {"detail": "Username updated successfully"}

@app.delete("/users/me")
def delete_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_user(db, current_user.id)
    return {"detail": "User deleted successfully"}

# Conversation endpoints
@app.get("/conversations/", response_model=List[Conversation])
def read_conversation_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = get_conversation_history(db, current_user.id)
    return conversations

@app.post("/conversations/")
def create_conversation(conversation: ConversationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_conversation = create_conversation(db, current_user.id, conversation.user_message, conversation.bot_response)
    return new_conversation

@app.post("/conversations/generate/")
def generate_recommendation(ingredients: str, current_user: User = Depends(get_current_user)):
    prompt = f"Based on the following ingredients: {ingredients}, please provide a food recommendation."
    recommendation = generate_food_recommendation(prompt)
    return {"recommendation": recommendation}

@app.delete("/conversations/")
def delete_conversation_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_conversation_history(db, current_user.id)
    return {"detail": "Conversation history deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
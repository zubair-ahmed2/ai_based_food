from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from config import DATABASE_URL



Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(String, default=datetime.utcnow)
    last_login = Column(String, default=datetime.utcnow)

class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    conversation = Column(Text, nullable=False)
    timestamp = Column(String, default=datetime.utcnow)

def init_db():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_conversation_history(db, user_id: int):
    return db.query(ConversationHistory).filter(ConversationHistory.user_id == user_id).all()

def get_user_by_id(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_conversation(db, user_id: int, user_message: str, bot_response: str):
    conversation = ConversationHistory(user_id=user_id, conversation=f"User: {user_message}\nBot: {bot_response}")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def delete_conversation_history(db, user_id: int):
    db.query(ConversationHistory).filter(ConversationHistory.user_id == user_id).delete()
    db.commit()

def create_user(db, username: str, email: str, hashed_password: str):
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db, user_id: int):
    db.query(User).filter(User.id == user_id).delete()
    db.commit()

def update_last_login(db, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def update_user_email(db, user_id: int, new_email: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.email = new_email
        db.commit()
        db.refresh(user)
    return user

def update_user_password(db, user_id: int, new_hashed_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = new_hashed_password
        db.commit()
        db.refresh(user)
    return user

def update_username(db, user_id: int, new_username: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.username = new_username
        db.commit()
        db.refresh(user)
    return user

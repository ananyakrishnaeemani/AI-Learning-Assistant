# backend/storage.py
import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edu.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

def init_db():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

def save_uploaded_file(file_obj, filename):
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file_obj.read())
    return path

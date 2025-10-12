# backend/main.py
import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlmodel import select
from storage import init_db, get_session, save_uploaded_file
from models import User, Progress, QuizResult
from auth import hash_password, verify_password, create_access_token, decode_token
import agents
from vector_store import add_pdf_to_vectorstore
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from pydantic import BaseModel



load_dotenv()
init_db()

app = FastAPI(title="LearnWise Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock to frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# Helper to extract user from Bearer token
# --------------------------------------------------------------------
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username = payload.get("sub")
    with get_session() as s:
        user = s.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

# --------------------------------------------------------------------
# Auth endpoints
# --------------------------------------------------------------------
@app.post("/signup")
def signup(username: str, password: str):
    with get_session() as s:
        existing = s.exec(select(User).where(User.username == username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="User exists")
        user = User(username=username, hashed_password=hash_password(password))
        s.add(user)
        s.commit()
        s.refresh(user)
        token = create_access_token({"sub": username})
        return {"token": token, "username": username}

@app.post("/login")
def login(username: str, password: str):
    with get_session() as s:
        user = s.exec(select(User).where(User.username == username)).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": username})
        return {"token": token, "username": username}

# --------------------------------------------------------------------
# Functional endpoints
# --------------------------------------------------------------------
@app.post("/upload_pdf")
def api_upload_pdf(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    path = save_uploaded_file(file.file, file.filename)

    # Add PDF content to vector DB
    n_chunks = add_pdf_to_vectorstore(path)

    return {"path": path, "chunks_added": n_chunks}


@app.post("/generate_syllabus")
def api_generate_syllabus(topic: str, user: User = Depends(get_current_user)):
    task = f"Generate a course syllabus to teach the topic: {topic}"
    syllabus = agents.gen_syllabus(topic, task)
    with get_session() as s:
        prog = s.exec(select(Progress).where(Progress.user_id == user.id, Progress.topic == topic)).first()
        if not prog:
            prog = Progress(user_id=user.id, topic=topic, completed_percent=0.0)
            s.add(prog)
        s.commit()
    return {"syllabus": syllabus}

@app.post("/generate_quiz")
def api_generate_quiz(topic: str, difficulty: str = "medium", n_questions: int = 5, user: User = Depends(get_current_user)):
    quiz = agents.generate_quiz(topic, difficulty, n_questions)
    return {"quiz": quiz}

@app.post("/submit_quiz")
def api_submit_quiz(topic: str, score: float, user: User = Depends(get_current_user)):
    with get_session() as s:
        qr = QuizResult(user_id=user.id, topic=topic, score=score)
        s.add(qr)
        prog = s.exec(select(Progress).where(Progress.user_id == user.id, Progress.topic == topic)).first()
        if not prog:
            prog = Progress(user_id=user.id, topic=topic, completed_percent=min(100.0, score))
            s.add(prog)
        else:
            prog.completed_percent = min(100.0, max(prog.completed_percent, score))
        s.commit()
    return {"ok": True}

class SubmitQuizRequest(BaseModel):
    topic: str
    quiz: list
    answers: list[int]

@app.post("/submit_quiz_answers")
def api_submit_quiz_answers(request: SubmitQuizRequest, user: User = Depends(get_current_user)):
    quiz = request.quiz
    answers = request.answers
    topic = request.topic

    if len(answers) != len(quiz):
        raise HTTPException(status_code=400, detail="Number of answers must match number of questions")

    correct = 0
    for i, q in enumerate(quiz):
        if answers[i] == q["correct_answer"]:
            correct += 1

    score = (correct / len(quiz)) * 100

    with get_session() as s:
        qr = QuizResult(user_id=user.id, topic=topic, score=score)
        s.add(qr)
        prog = s.exec(select(Progress).where(Progress.user_id == user.id, Progress.topic == topic)).first()
        if not prog:
            prog = Progress(user_id=user.id, topic=topic, completed_percent=min(100.0, score))
            s.add(prog)
        else:
            prog.completed_percent = min(100.0, max(prog.completed_percent, score))
        s.commit()

    return {"score": score, "correct": correct, "total": len(quiz)}

@app.post("/chat")
def api_chat(message: str, user: User = Depends(get_current_user)):
    response = agents.instructor_step(message)
    return {"response": response}

@app.get("/progress")
def api_progress(user: User = Depends(get_current_user)):
    with get_session() as s:
        rows = s.exec(select(Progress).where(Progress.user_id == user.id)).all()
        return {"progress": [r.dict() for r in rows]}

class ChatRequest(BaseModel):
    message: str

@app.post("/rag_chat")
def rag_chat(request: ChatRequest, user: User = Depends(get_current_user)):
    """Chat with uploaded PDFs using RAG (retrieval-augmented generation)."""
    from vector_store import VECTOR_DB_PATH

    if not os.path.exists(VECTOR_DB_PATH):
        raise HTTPException(status_code=400, detail="No PDFs indexed yet. Please upload first.")

    embeddings = FastEmbedEmbeddings()
    vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )

    response = qa_chain.invoke({"query": request.message})
    return {"response": response}

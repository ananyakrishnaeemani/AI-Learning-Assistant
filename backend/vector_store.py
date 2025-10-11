# CORRECTED: Switched to a free, high-performance embedding model
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import os
import pickle

VECTOR_DB_PATH = "backend/faiss_index.pkl"

# Load or create FAISS index
def load_vectorstore():
    if os.path.exists(VECTOR_DB_PATH):
        with open(VECTOR_DB_PATH, "rb") as f:
            # allow_dangerous_deserialization is needed for FAISS with pickle
            vectorstore = pickle.load(f)
    else:
        vectorstore = None
    return vectorstore

def save_vectorstore(vectorstore):
    with open(VECTOR_DB_PATH, "wb") as f:
        pickle.dump(vectorstore, f)

# Extract text from PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# Split text and create embeddings
def add_pdf_to_vectorstore(file_path):
    text = extract_text_from_pdf(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_text(text)
    
    # Use FastEmbed for free, local, and fast embeddings
    embeddings = FastEmbedEmbeddings()
    
    # Load existing store or create a new one
    if os.path.exists(VECTOR_DB_PATH):
        vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_texts(docs)
    else:
        vectorstore = FAISS.from_texts(docs, embeddings)
    
    # Save the updated vector store
    vectorstore.save_local(VECTOR_DB_PATH)
    
    return len(docs)

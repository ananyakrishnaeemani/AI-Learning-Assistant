import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def auth_header(token: str):
    """Return the Authorization header if a token is provided."""
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

# ---------------- Signup/Login ----------------
def signup(username, password):
    url = f"{BASE_URL}/signup"
    params = {"username": username, "password": password}
    try:
        resp = requests.post(url, params=params)
        resp.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Signup request failed: {e}")
        # Try to parse error from response, otherwise return a generic error
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}

def login(username, password):
    url = f"{BASE_URL}/login"
    params = {"username": username, "password": password}
    try:
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}

# ---------------- Upload PDF ----------------
def upload_pdf(file_obj, token: str):
    url = f"{BASE_URL}/upload_pdf"
    headers = auth_header(token)
    if not headers:
        return {"error": "Authentication required. Please login first."}

    with open(file_obj.name, "rb") as f:
        files = {"file": (os.path.basename(file_obj.name), f, "application/pdf")}
        try:
            resp = requests.post(url, files=files, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Upload PDF request failed: {e}")
            try:
                return e.response.json() if e.response else {"error": str(e)}
            except ValueError:
                return {"error": "Failed to connect to the server or parse error response."}


def rag_chat(query, token: str):
    url = f"{BASE_URL}/rag_chat"
    headers = auth_header(token)
    try:
        resp = requests.post(url, json={"message": query}, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"RAG chat request failed: {e}")
        return {"error": str(e)}

# ---------------- Generate Syllabus ----------------
def generate_syllabus(topic: str, token: str):
    url = f"{BASE_URL}/generate_syllabus"
    headers = auth_header(token)
    if not headers:
        return {"error": "Authentication required. Please login first."}
    params = {"topic": topic}
    try:
        resp = requests.post(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Generate syllabus request failed: {e}")
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}

# ---------------- Generate Quiz ----------------
def generate_quiz(topic: str, difficulty: str, n_questions: int, token: str):
    url = f"{BASE_URL}/generate_quiz"
    headers = auth_header(token)
    if not headers:
        return {"error": "Authentication required. Please login first."}
    params = {"topic": topic, "difficulty": difficulty, "n_questions": n_questions}
    try:
        resp = requests.post(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Generate quiz request failed: {e}")
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}

# ---------------- Chat with Instructor ----------------
def chat(message: str, token: str):
    url = f"{BASE_URL}/chat"
    headers = auth_header(token)
    if not headers:
        return {"error": "Authentication required. Please login first."}
    params = {"message": message}
    try:
        resp = requests.post(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Chat request failed: {e}")
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}

# ---------------- Get Progress ----------------
def get_progress(token: str):
    url = f"{BASE_URL}/progress"
    headers = auth_header(token)
    if not headers:
        return {"error": "Authentication required. Please login first."}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Get progress request failed: {e}")
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}

# ---------------- Submit Quiz Answers ----------------
def submit_quiz_answers(topic: str, quiz: list, answers: list, token: str):
    url = f"{BASE_URL}/submit_quiz_answers"
    headers = auth_header(token)
    if not headers:
        return {"error": "Authentication required. Please login first."}
    data = {"topic": topic, "quiz": quiz, "answers": answers}
    try:
        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Submit quiz answers request failed: {e}")
        try:
            return e.response.json() if e.response else {"error": str(e)}
        except ValueError:
            return {"error": "Failed to connect to the server or parse error response."}


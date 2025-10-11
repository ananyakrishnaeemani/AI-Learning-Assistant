# frontend/utils/auth.py
token = ""

def set_token(t):
    global token
    token = t

def get_token():
    global token
    return token

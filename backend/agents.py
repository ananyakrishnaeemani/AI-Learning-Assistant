import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

# It's good practice to keep imports at the top
from generating_syllabus import generate_syllabus as gen_syllabus
from teaching_agent import teaching_agent

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def generate_quiz(topic: str, difficulty: str = "medium", n_questions: int = 5) -> dict:
    """
    Generates multiple-choice questions for a given topic using an LLM.
    This function is now more robust against formatting errors from the LLM.
    """
    if not groq_api_key:
        return {"error": "GROQ_API_KEY not found. Please set it in your .env file."}

    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key, temperature=0.3)
    
    # A more detailed prompt improves the chances of getting good JSON
    prompt = (
        f"Generate exactly {n_questions} multiple-choice questions about the topic: '{topic}'.\n"
        f"The difficulty level should be {difficulty}.\n"
        "For each question, provide a 'question' text, an array of 4 'choices', "
        "and the 0-indexed integer for the 'correct_answer'.\n"
        "IMPORTANT: Your response MUST be a valid JSON list of objects and nothing else. "
        "Do not include any introductory text, markdown formatting, or explanations."
        "Example format: "
        '[{"question": "What is 2+2?", "choices": ["3", "4", "5", "6"], "correct_answer": 1}]'
    )

    try:
        msg = HumanMessage(content=prompt)
        resp = llm.invoke([msg])
        response_content = resp.content

        # --- NEW: Robust JSON Parsing ---
        # 1. Use a regular expression to find the JSON block (list or object)
        json_match = re.search(r'\[.*\]|\{.*\}', response_content, re.DOTALL)
        
        if not json_match:
            # If no JSON is found at all, return an error with the raw response
            return {"error": "Failed to find valid JSON in the LLM response.", "raw_response": response_content}

        json_string = json_match.group(0)
        
        # 2. Try to parse the extracted string
        parsed_json = json.loads(json_string)
        return parsed_json

    except json.JSONDecodeError:
        # This catches errors if the extracted string is still not valid JSON
        return {"error": "Failed to decode JSON from the LLM response.", "extracted_string": json_string}
    except Exception as e:
        # This catches other potential errors (e.g., API call failure)
        print(f"An unexpected error occurred in generate_quiz: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

def seed_teaching_agent(syllabus: str, task: str):
    teaching_agent.seed_agent(syllabus, task)

def instructor_step(user_message: str):
    # record user message and ask instructor to respond
    teaching_agent.human_step(user_message)
    return teaching_agent.instructor_step()

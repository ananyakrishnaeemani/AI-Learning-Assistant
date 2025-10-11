import gradio as gr
from frontend.utils.api_calls import generate_quiz

def quiz_ui(auth_token_state: gr.State):
    """Creates the UI for generating a quiz."""
    with gr.Blocks() as interface:
        with gr.Row():
            topic_input = gr.Textbox(label="Topic", placeholder="e.g., Python Data Structures")
            difficulty_input = gr.Dropdown(["easy", "medium", "hard"], label="Difficulty", value="medium")
            n_questions_input = gr.Number(label="Number of Questions", value=5, step=1, minimum=1, maximum=10)
        
        generate_btn = gr.Button("Generate Quiz", variant="primary")
        output_json = gr.JSON(label="Quiz Questions")
        output_text = gr.Textbox(label="Status")

        def handle_generate_quiz(topic, difficulty, n_questions, token):
            if not token:
                gr.Warning("Please login to generate a quiz.")
                return None, "Login required."
            if not topic:
                gr.Warning("Please enter a topic for the quiz.")
                return None, "Topic is required."

            response = generate_quiz(topic, difficulty, int(n_questions), token)
            
            # --- NEW: Defensive check for None ---
            # This check will prevent the 'NoneType' attribute error crash.
            if response is None:
                error_msg = "Received no response from the server. The backend might be down or have an error."
                gr.Error(error_msg)
                return None, error_msg

            if "error" in response:
                return None, f"Error: {response['error']}"
            
            quiz_data = response.get("quiz")
            if not quiz_data:
                 return None, f"Failed to parse quiz from response: {response}"

            return quiz_data, "Quiz generated successfully!"

        generate_btn.click(
            handle_generate_quiz, 
            inputs=[topic_input, difficulty_input, n_questions_input, auth_token_state], 
            outputs=[output_json, output_text]
        )
    return interface


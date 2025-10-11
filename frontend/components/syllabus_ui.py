import gradio as gr
from frontend.utils.api_calls import generate_syllabus

def syllabus_ui(auth_token_state: gr.State):
    """Creates the UI for generating a course syllabus."""
    with gr.Blocks() as interface:
        topic_input = gr.Textbox(label="Topic", placeholder="e.g., Introduction to Machine Learning")
        generate_btn = gr.Button("Generate Syllabus", variant="primary")
        output_markdown = gr.Markdown(label="Generated Syllabus")
        output_text = gr.Textbox(label="Status")

        def handle_generate_syllabus(topic, token):
            if not token:
                gr.Warning("Please login to generate a syllabus.")
                return None, "Login required."
            if not topic:
                gr.Warning("Please enter a topic.")
                return None, "Topic is required."

            response = generate_syllabus(topic, token)
            
            if response and "error" in response:
                return None, f"Error: {response['error']}"

            syllabus_content = response.get("syllabus", "Could not find syllabus in response.")
            return syllabus_content, "Syllabus generated successfully!"

        generate_btn.click(
            handle_generate_syllabus, 
            inputs=[topic_input, auth_token_state], 
            outputs=[output_markdown, output_text]
        )
    return interface

import gradio as gr
import pandas as pd
from frontend.utils.api_calls import get_progress

def progress_ui(auth_token_state: gr.State):
    """Creates the UI for displaying user progress."""
    with gr.Blocks() as interface:
        refresh_btn = gr.Button("Refresh Progress", variant="primary")
        # Using a DataFrame for a clean, tabular view of progress
        output_dataframe = gr.DataFrame(label="Your Progress")
        output_text = gr.Textbox(label="Status")

        def handle_get_progress(token):
            if not token:
                gr.Warning("Please login to see your progress.")
                return None, "Login required."

            response = get_progress(token)

            if response and "error" in response:
                return None, f"Error: {response['error']}"

            progress_data = response.get("progress")
            if not progress_data:
                return None, "No progress data found."

            # Convert the list of dicts to a pandas DataFrame for display
            df = pd.DataFrame(progress_data)
            return df, "Progress updated successfully."

        refresh_btn.click(
            handle_get_progress, 
            inputs=[auth_token_state], 
            outputs=[output_dataframe, output_text]
        )
    return interface

import gradio as gr
from frontend.components.login_ui import login_ui
from frontend.components.syllabus_ui import syllabus_ui
from frontend.components.quiz_ui import quiz_ui
from frontend.components.chat_ui import chat_ui
from frontend.components.upload_ui import upload_ui
from frontend.components.progress_ui import progress_ui


def main():
    with gr.Blocks(theme=gr.themes.Soft(), title="LearnWise") as app:
        gr.Markdown("# LearnWise - AI Learning Platform")

        # This invisible component will store the session token for each user
        # We initialize it with None, as the user is not logged in initially.
        auth_token_state = gr.State(value=None)
        
        with gr.Tab("Login / Signup"):
            # Pass the state object to the login UI so it can be updated
            login_ui(auth_token_state)
        
        with gr.Tab("Upload PDF"):
            # Pass the state object to every other component that needs authentication
            upload_ui(auth_token_state)

        with gr.Tab("Generate Syllabus"):
            syllabus_ui(auth_token_state)
        
        with gr.Tab("Chat with Instructor"):
            chat_ui(auth_token_state)

        with gr.Tab("Generate Quiz"):
            quiz_ui(auth_token_state)
        
        with gr.Tab("Progress"):
            progress_ui(auth_token_state)
    
    app.launch()

if __name__ == "__main__":
    main()

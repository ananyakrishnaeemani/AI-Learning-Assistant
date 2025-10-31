import gradio as gr
from frontend.utils.api_calls import rag_chat

def chat_ui(auth_token_state: gr.State):
    # The chatbot component displays the conversation history
    chatbot = gr.Chatbot(label="Instructor Chat", type="messages", height=500)
    
    message_input = gr.Textbox(label="Your Message", placeholder="Ask the instructor a question...")
    send_btn = gr.Button("Send")

    # This state will store the conversation history for the session
    chat_history_state = gr.State(value=[])

    def handle_chat(user_message: str, history: list, token: str):
        if not token:
            gr.Warning("You must be logged in to chat!")
            return history, history # Return history unchanged

        # Append user message to the history
        history.append({"role": "user", "content": user_message})

        # We yield the history here to show the user's message in the UI immediately
        yield history, history

        # Call the backend API
        response_data = rag_chat(user_message, token)
        ai_response = response_data.get("response", "Error: No response from server.")

        # Append the AI's response to the history
        history.append({"role": "assistant", "content": ai_response})

        # Yield the final history
        yield history, history

    send_btn.click(
        handle_chat,
        inputs=[message_input, chat_history_state, auth_token_state],
        outputs=[chatbot, chat_history_state]
    ).then(lambda: gr.update(value=""), outputs=[message_input]) # Clear the input box after sending

import gradio as gr
from frontend.utils.api_calls import upload_pdf, rag_chat


def upload_ui(auth_token_state):
    """
    Combined Upload + Chat UI for EduGPT
    """

    gr.Markdown("## 📘 Upload Study Material & Chat with AI Tutor")

    # Store uploaded file name for RAG context
    uploaded_file_name = gr.State(value=None)

    with gr.Row():
        file_input = gr.File(label="Upload your PDF file", file_types=[".pdf"])
        upload_btn = gr.Button("📤 Upload PDF", variant="primary")

    upload_status = gr.Markdown(value="")

    # ---- Chat Components ----
    chatbot = gr.Chatbot(label="Chat with your uploaded material", type="messages", height=400)
    chat_input = gr.Textbox(
        placeholder="Ask something from your PDF...", 
        label="Your question", 
        visible=False
    )
    send_btn = gr.Button("Send", visible=False)

    # --------------- Handlers ---------------

    def handle_upload(file_obj, token):
        if not token:
            return "❌ Please login first.", gr.update(visible=False), gr.update(visible=False)

        if file_obj is None:
            return "⚠️ Please upload a PDF file first.", gr.update(visible=False), gr.update(visible=False)

        result = upload_pdf(file_obj, token)
        if "error" in result:
            return f"❌ Upload failed: {result['error']}", gr.update(visible=False), gr.update(visible=False)

        filename = result.get("filename", file_obj.name)
        success_msg = f"✅ PDF uploaded successfully: **{filename}**\nNow you can chat below ⬇️"
        return success_msg, gr.update(visible=True), gr.update(visible=True), filename

    def handle_chat(user_msg, history, token, filename):
        if not token:
            new_history = history + [{"role": "user", "content": user_msg}, {"role": "assistant", "content": "⚠️ Please login first."}]
            return new_history
        if not filename:
            new_history = history + [{"role": "user", "content": user_msg}, {"role": "assistant", "content": "⚠️ Please upload a PDF first."}]
            return new_history

        # Add user message
        new_history = history + [{"role": "user", "content": user_msg}, {"role": "assistant", "content": "⌛ Thinking..."}]

        response = rag_chat(user_msg, token)
        answer = response.get("response", "⚠️ Error generating response.")
        new_history[-1]["content"] = answer
        return new_history

    # --------------- Events ---------------
    upload_btn.click(
        handle_upload,
        inputs=[file_input, auth_token_state],
        outputs=[upload_status, chat_input, send_btn, uploaded_file_name],
    )

    send_btn.click(
        handle_chat,
        inputs=[chat_input, chatbot, auth_token_state, uploaded_file_name],
        outputs=[chatbot],
    )


# End of file

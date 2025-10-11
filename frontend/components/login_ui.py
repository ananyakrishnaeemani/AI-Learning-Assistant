import gradio as gr
from frontend.utils.api_calls import login, signup

# Accept the state object as an argument
def login_ui(auth_token_state: gr.State):
    with gr.Row():
        username_input = gr.Textbox(label="Username", placeholder="Enter your username")
        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
    
    with gr.Row():
        login_btn = gr.Button("Login")
        signup_btn = gr.Button("Signup")
        
    output = gr.Textbox(label="Status", interactive=False)
    
    # This function will handle the login logic
    def handle_login(username, password):
        if not username or not password:
            return "Username and password are required.", None
        data = login(username, password)
        if "token" in data:
            # On successful login, return the success message AND the new token
            # Gradio will update the `output` textbox and the `auth_token_state`
            return f"Login successful for {data.get('username')}!", data["token"]
        else:
            return data.get("detail", "Login failed."), None

    # This function will handle the signup logic
    def handle_signup(username, password):
        if not username or not password:
            return "Username and password are required.", None
        data = signup(username, password)
        if "token" in data:
            # On successful signup, update the state with the new token
            return f"Signup successful for {data.get('username')}! You are now logged in.", data["token"]
        else:
            return data.get("detail", "Signup failed."), None
    
    # The `click` event now updates TWO components: the visible `output` textbox
    # and the invisible `auth_token_state`
    login_btn.click(
        handle_login, 
        inputs=[username_input, password_input], 
        outputs=[output, auth_token_state]
    )
    signup_btn.click(
        handle_signup, 
        inputs=[username_input, password_input], 
        outputs=[output, auth_token_state]
    )

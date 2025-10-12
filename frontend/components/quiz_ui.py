import gradio as gr
from frontend.utils.api_calls import generate_quiz, submit_quiz_answers

def quiz_ui(auth_token_state: gr.State):
    """Creates the UI for generating and taking a quiz."""
    with gr.Blocks() as interface:
        topic_state = gr.State(value="")  # Store the quiz topic
        quiz_state = gr.State(value=None)  # Store the generated quiz

        with gr.Row():
            topic_input = gr.Textbox(label="Topic", placeholder="e.g., Python Data Structures")
            difficulty_input = gr.Dropdown(["easy", "medium", "hard"], label="Difficulty", value="medium")
            n_questions_input = gr.Number(label="Number of Questions", value=5, step=1, minimum=1, maximum=10)

        generate_btn = gr.Button("Generate Quiz", variant="primary")
        quiz_display = gr.Markdown(label="Quiz Questions")
        answers_input = gr.Textbox(
            label="Your Answers",
            placeholder="Enter answer indices separated by commas (e.g., 0,2,1,3,0)",
            lines=2,
            visible=False
        )
        submit_btn = gr.Button("Submit Quiz", variant="secondary", visible=False)
        result_display = gr.Markdown(label="Quiz Result")
        output_text = gr.Textbox(label="Status")

        def handle_generate_quiz(topic, difficulty, n_questions, token):
            if not token:
                gr.Warning("Please login to generate a quiz.")
                return None, "", False, False, "", "Login required."
            if not topic:
                gr.Warning("Please enter a topic for the quiz.")
                return None, "", False, False, "", "Topic is required."

            response = generate_quiz(topic, difficulty, int(n_questions), token)

            if response is None:
                error_msg = "Received no response from the server. The backend might be down or have an error."
                gr.Error(error_msg)
                return None, "", False, False, "", error_msg

            if "error" in response:
                return None, "", False, False, "", f"Error: {response['error']}"

            quiz_data = response.get("quiz")
            if not quiz_data:
                 return None, "", False, False, "", f"Failed to parse quiz from response: {response}"

            # Format quiz for display
            quiz_md = f"## Quiz: {topic}\n\n"
            for i, q in enumerate(quiz_data):
                quiz_md += f"**{i+1}. {q['question']}**\n"
                for j, choice in enumerate(q['choices']):
                    quiz_md += f"{j}. {choice}\n"
                quiz_md += "\n"

            instructions = f"Enter your answers as indices (0-3) separated by commas. For example: 0,2,1,3,0 for {len(quiz_data)} questions."
            answers_placeholder = f"Enter {len(quiz_data)} answers separated by commas"

            return quiz_data, quiz_md, True, True, "", f"Quiz generated! {instructions}"

        def handle_submit_quiz(quiz, answers_text, token):
            if not token:
                return "", "Login required."
            if not quiz:
                return "", "No quiz generated."
            if not answers_text.strip():
                return "", "Please enter your answers."

            try:
                # Parse answers from comma-separated string
                answer_indices = [int(x.strip()) for x in answers_text.split(',')]
            except ValueError:
                return "", "Invalid answer format. Please enter numbers separated by commas."

            if len(answer_indices) != len(quiz):
                return "", f"Please provide exactly {len(quiz)} answers."

            response = submit_quiz_answers(topic_state.value, quiz, answer_indices, token)

            if "error" in response:
                return "", f"Error: {response['error']}"

            score = response.get("score", 0)
            correct = response.get("correct", 0)
            total = response.get("total", 0)

            result_md = f"## Quiz Result\n\n"
            result_md += f"**Score: {score:.1f}%**\n\n"
            result_md += f"**Correct Answers: {correct}/{total}**\n\n"

            if score >= 80:
                result_md += "🎉 Excellent work!"
            elif score >= 60:
                result_md += "👍 Good job! Keep practicing."
            else:
                result_md += "📚 Keep studying and try again!"

            return result_md, "Quiz submitted successfully!"

        generate_btn.click(
            handle_generate_quiz,
            inputs=[topic_input, difficulty_input, n_questions_input, auth_token_state],
            outputs=[quiz_state, quiz_display, answers_input, submit_btn, result_display, output_text]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[answers_input]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[submit_btn]
        )

        # Store topic when generating quiz
        generate_btn.click(
            lambda topic: topic,
            inputs=[topic_input],
            outputs=[topic_state]
        )

        submit_btn.click(
            handle_submit_quiz,
            inputs=[quiz_state, answers_input, auth_token_state],
            outputs=[result_display, output_text]
        )

    return interface


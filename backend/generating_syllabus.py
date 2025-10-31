import os
from typing import List
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)


# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


# Define a Discuss agent class
class DiscussAgent:
    def __init__(
        self,
        system_message: SystemMessage,
        model: ChatGroq,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.init_messages()

    def reset(self) -> None:
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        self.stored_messages.append(message)
        return self.stored_messages

    def step(
        self,
        input_message: HumanMessage,
    ) -> AIMessage:
        messages = self.update_messages(input_message)

        output_message = self.model.invoke(messages)
        self.update_messages(output_message)

        return output_message


# Set up roles
assistant_role_name = "Instructor"
user_role_name = "Teaching Assistant"

word_limit = 50  # word limit for task brainstorming

# Create inception prompts
assistant_inception_prompt = """Never forget you are a {assistant_role_name} and I am a {user_role_name}. Never flip roles! ...
Here is the task: {task}. Never forget our task!
Solution: <YOUR_SOLUTION>
Next request."""

user_inception_prompt = """Never forget you are a {user_role_name} and I am a {assistant_role_name}. Never flip roles! ...
When the task is completed, you must only reply with a single word <TASK_DONE>."""


# Get message from system
def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
    assistant_sys_template = SystemMessagePromptTemplate.from_template(
        template=assistant_inception_prompt
    )
    assistant_sys_msg = assistant_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    user_sys_template = SystemMessagePromptTemplate.from_template(
        template=user_inception_prompt
    )
    user_sys_msg = user_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    return assistant_sys_msg, user_sys_msg


# Create a task specify agent
task_specifier_sys_msg = SystemMessage(
    content="You can make a task more specific."
)
task_specifier_prompt = """Here is a task that {assistant_role_name} will help {user_role_name} to complete: {task}.
Please make it more specific. Be creative and imaginative.
Please reply with the specified task in {word_limit} words or less. Do not add anything else."""
task_specifier_template = HumanMessagePromptTemplate.from_template(
    template=task_specifier_prompt
)
task_specify_agent = DiscussAgent(
    task_specifier_sys_msg, ChatGroq(model="llama-3.1-8b-instant",groq_api_key=groq_api_key)
)


# Optimized function to generate the syllabus with a single LLM call
def generate_syllabus(topic, task):
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key, temperature=0.3)

    prompt = f"""
    Generate a comprehensive course syllabus for the topic: "{topic}".

    The syllabus should include:
    1. Course Title
    2. Course Description
    3. Learning Objectives
    4. Prerequisites (if any)
    5. Course Outline with modules/weeks
    6. Assessment Methods
    7. Required Materials/Resources

    Make it detailed but concise, suitable for a beginner to intermediate level course.
    Format it in a clear, structured manner.
    """

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return response.content

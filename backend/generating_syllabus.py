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


# Function to generating the syllabus
def generate_syllabus(topic, task):
    task_specifier_msg = task_specifier_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
        word_limit=word_limit,
    )[0]
    specified_task_msg = task_specify_agent.step(task_specifier_msg)
    specified_task = specified_task_msg.content
    assistant_sys_msg, user_sys_msg = get_sys_msgs(
        assistant_role_name, user_role_name, specified_task
    )

    assistant_agent = DiscussAgent(
        assistant_sys_msg, ChatGroq(model="llama-3.1-8b-instant",groq_api_key=groq_api_key)
    )
    user_agent = DiscussAgent(
        user_sys_msg, ChatGroq(model="llama-3.1-8b-instant",groq_api_key=groq_api_key)
    )

    assistant_agent.reset()
    user_agent.reset()

    assistant_msg = HumanMessage(
        content=(f"{user_sys_msg.content}. Start instructions.")
    )

    user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
    user_msg = assistant_agent.step(user_msg)

    print(f"Specified task prompt:\n{specified_task}\n")
    conversation_history = []

    chat_turn_limit, n = 5, 0
    while n < chat_turn_limit:
        n += 1
        user_ai_msg = user_agent.step(assistant_msg)
        user_msg = HumanMessage(content=user_ai_msg.content)

        print(f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n")
        conversation_history.append("AI User:" + user_msg.content)

        assistant_ai_msg = assistant_agent.step(user_msg)
        assistant_msg = HumanMessage(content=assistant_ai_msg.content)
        conversation_history.append("AI Assistant:" + assistant_msg.content)

        print(f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n")
        if "<TASK_DONE>" in user_msg.content:
            break

    summarizer_sys_msg = SystemMessage(
        content=f"Summarize this conversation into a {topic} course syllabus form"
    )
    summarizer_prompt = """Here is a conversation history: {conversation_history}.
    Please summarize into a course syllabus form with the topic from user input."""
    summarizer_template = HumanMessagePromptTemplate.from_template(
        template=summarizer_prompt
    )
    summarizer_agent = DiscussAgent(
        summarizer_sys_msg, ChatGroq(model="llama-3.1-8b-instant",groq_api_key=groq_api_key)
    )
    summarizer_msg = summarizer_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        conversation_history=conversation_history,
    )[0]
    summarizered_msg = summarizer_agent.step(summarizer_msg)
    return summarizered_msg.content

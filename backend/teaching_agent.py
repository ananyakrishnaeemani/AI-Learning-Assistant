import os
from typing import Any, Dict, List
from dotenv import load_dotenv

# CORRECTED IMPORTS: LLMChain and PromptTemplate have moved to new locations
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.llms.base import BaseLLM
from pydantic import BaseModel, Field

# Load env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


class InstructorConversationChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        instructor_agent_inception_prompt = """
        As a Machine Learning instructor agent, your task is to teach the user based on a provided syllabus.
        ===
        {syllabus}
        ===
        {conversation_history}
        ===
        """
        prompt = PromptTemplate(
            template=instructor_agent_inception_prompt,
            input_variables=["syllabus", "topic", "conversation_history"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class TeachingGPT(BaseModel):
    syllabus: str = ""
    conversation_topic: str = ""
    conversation_history: List[str] = []
    teaching_conversation_utterance_chain: InstructorConversationChain = Field(...)

    def seed_agent(self, syllabus, task):
        self.syllabus = syllabus
        self.conversation_topic = task
        self.conversation_history = []

    def human_step(self, human_input):
        human_input = human_input + "<END_OF_TURN>"
        self.conversation_history.append(human_input)

    def instructor_step(self):
        return self._callinstructor(inputs={})

    def _callinstructor(self, inputs: Dict[str, Any]) -> None:
        ai_message = self.teaching_conversation_utterance_chain.run(
            syllabus=self.syllabus,
            topic=self.conversation_topic,
            conversation_history="\n".join(self.conversation_history),
        )
        self.conversation_history.append(ai_message)
        print("Instructor: ", ai_message.rstrip("<END_OF_TURN>"))
        return ai_message

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "TeachingGPT":
        teaching_conversation_utterance_chain = InstructorConversationChain.from_llm(
            llm, verbose=verbose
        )
        return cls(
            teaching_conversation_utterance_chain=teaching_conversation_utterance_chain,
            **kwargs,
        )


# Teaching agent instance
config = dict(conversation_history=[], syllabus="", conversation_topic="")
llm = ChatGroq(model="llama-3.1-8b-instant",groq_api_key=groq_api_key, temperature=0.9)
teaching_agent = TeachingGPT.from_llm(llm, **config)

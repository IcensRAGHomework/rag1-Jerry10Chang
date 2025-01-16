import json
import traceback

from model_configurations import get_model_configuration

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)


from typing import Union, Optional
from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel, Field

    
class Holidy(BaseModel):
    date: str =  Field(description="The date of the holiday")
    name: str = Field(description="The name of the holiday")

class Resule_Holidy(BaseModel):
    Result: list[Holidy]# = Field(description="The result of the holiday")
    

class Joke(BaseModel):
    """Joke to tell user."""

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10"
    )


def generate_hw01(question):
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    '''
    examples = [
        {
            "human": "{question}",
            "Result":[
                {
                    "date": "2024-1-1",
                    "name": "元旦"
                },
                {
                    "date": "2024-2-28",
                    "name": "和平紀念日"
                }
            ]
        }
    ]

    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}")
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是行事曆"),
            few_shot_prompt,
        ]
    )
    '''

    system = """你是行事曆"""
    # Here are some examples of holidays:
    # example_user: "2024年台灣1月紀念日有哪些?"
    # example_system: {"Result":[{"date":"2024-1-1","name":"元旦"}}
    # example_user: "2024年台灣2月紀念日有哪些?"
    # example_system: {"Result":[{"date":"2024-2-28","name":"和平紀念日"}]}
    # """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}")
        ]
    )
    structured_llm = llm.with_structured_output(Resule_Holidy)
    chain = prompt | structured_llm
    message = {"question": question}
    response = chain.invoke(message) #.to_messages()

    return str(response.dict())
    
def generate_hw02(question):
    pass
    
def generate_hw03(question2, question3):
    pass
    
def generate_hw04(question):
    pass
    
def demo(question):
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    message = HumanMessage(
            content=[
                {"type": "text", "text": question},
            ]
    )
    response = llm.invoke([message])
    
    return response
# print(demo("2024年台灣10月紀念日有哪些?"))

print(generate_hw01("2024年台灣10月紀念日有哪些?"))

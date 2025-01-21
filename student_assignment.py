import json
import traceback

from model_configurations import get_model_configuration

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)


from typing import Union, Optional
from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel, Field

import requests

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage, AIMessage
from typing import List

class Holidy(BaseModel):
    date: str =  Field(description="The date of the holiday")
    name: str = Field(description="The name of the holiday")

class Result_Holidy(BaseModel):
    Result: list[Holidy] = Field(description="The result of the holiday")

class YearsCountryMonth(BaseModel):
    year: int = Field(description="The year of the holiday")
    country: str = Field(description="The country of the holiday")
    month: int = Field(description="The month of the holiday")

class Result_YearsCountryMonth(BaseModel):
    Result: list[YearsCountryMonth] = Field(description="The result of the message")

class YesNoReason(TypedDict):
    add: str = Field(description="true or false")
    reason: str = Field(description="The reason of the answer, and show the holidays in the existing list")

class Result_AddReason(TypedDict):
    Result: list[YesNoReason] = Field(description="The result of the message")

def llm_config():
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    return llm

store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

def generate_hw01(question):
    llm = llm_config()

    system = """你是一個行事曆"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}")
        ]
    )
    structured_llm = llm.with_structured_output(Result_Holidy)
    chain = prompt | structured_llm
    message = {"question": question}
    response = chain.invoke(message) #.to_messages()

    return json.dumps(response.dict())
    
def generate_hw02(question):
    llm = llm_config()

    system = """你是一個行事曆，請根據問題回答出指定的年份、國家、月份，其中國家請用iso-3166 format回答"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}")
        ]
    )
    structured_llm = llm.with_structured_output(Result_YearsCountryMonth)
    chain = prompt | structured_llm
    message = {"question": question}
    response = chain.invoke(message)
    response_year = response.dict()['Result'][0]['year']
    response_country = response.dict()['Result'][0]['country']
    response_month = response.dict()['Result'][0]['month']

    # Get the holidays from the API
    API_KEY = "CuVn6mmYwNFutCyLkRPepSSyk1szOeyQ"
    API_Base_URL = "https://calendarific.com/api/v2"
    API_Endpoints = "/holidays"
    API_URL = f"{API_Base_URL}{API_Endpoints}?api_key={API_KEY}&country={response_country}&language=zh&year={response_year}&month={response_month}"
    API_reponse = requests.get(API_URL).json()
    
    final_json_response = {}
    tmp_array = []
    for holiday in API_reponse['response']['holidays']:
        tmp_array.append({"date": holiday['date']['iso'], "name": holiday['name']})
    final_json_response['Result'] = tmp_array
    return json.dumps(final_json_response)

def generate_hw03(question2, question3):
    feedback_hw2 = generate_hw02(question2)
    holidays = json.loads(feedback_hw2).get("Result", [])

    llm = llm_config()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system}"),
            ("ai", "{holidays}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
            
        ]
    )

    structured_llm = llm.with_structured_output(Result_AddReason)
    chain = prompt | structured_llm

    agent_with_chat_history = RunnableWithMessageHistory(
        chain,
        get_by_session_id,
        input_messages_key="question",
        history_messages_key="history",
    )
    system = "你是一個中文行事曆，請依照格式回答問題。add : 這是一個布林值，表示是否需要將節日新增到節日清單中。根據問題判斷該節日是否存在於清單中，如果不存在，則為 true；否則為 false。reason : 描述為什麼需要或不需要新增節日，具體說明是否該節日已經存在於清單中，以及當前清單的內容。"
    message_hw3 = {"question": question3, "system": system, "holidays": holidays}
    response_hw3 = agent_with_chat_history.invoke(message_hw3, config={"configurable": {"session_id": "foo"}})
    return json.dumps(response_hw3)


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

# HW1
# answer = generate_hw01("2024年台灣10月紀念日有哪些?")
# print(json.loads(answer))

# HW2
answer = generate_hw03("2024年台灣10月紀念日有哪些?", '根據先前的節日清單，這個節日{"date": "10-31", "name": "蔣公誕辰紀念日"}是否有在該月份清單？')
print(json.loads(answer))

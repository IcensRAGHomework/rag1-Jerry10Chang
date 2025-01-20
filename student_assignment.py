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

import requests
    
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

    # Get the year, country, month from the question
    API_KEY = "CuVn6mmYwNFutCyLkRPepSSyk1szOeyQ"
    API_Base_URL = "https://calendarific.com/api/v2"
    API_Endpoints = "/holidays"
    
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
    print(response_year, response_country, response_month)
    # Get the holidays from the API
    API_URL = f"{API_Base_URL}{API_Endpoints}?api_key={API_KEY}&country={response_country}&year={response_year}&month={response_month}"
    API_reponse = requests.get(API_URL).json()
    
    final_json_response = {}
    tmp_array = []
    for holiday in API_reponse['response']['holidays']:
        tmp_array.append({"date": holiday['date']['iso'], "name": holiday['name']})
    final_json_response['Result'] = tmp_array
    return json.dumps(final_json_response)

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

# HW1
# answer = generate_hw01("2024年台灣10月紀念日有哪些?")
# print(json.loads(answer))

# HW2
answer = generate_hw02("2024年台灣10月紀念日有哪些?")
print(answer)

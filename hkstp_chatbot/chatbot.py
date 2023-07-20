import openai
from termcolor import colored
import streamlit as st
import configparser
import logging
from langchain import LLMMathChain, OpenAI, SerpAPIWrapper, SQLDatabase, SQLDatabaseChain
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

from database import get_redis_connection, get_redis_results

from config import CHAT_MODEL, COMPLETIONS_MODEL, INDEX_NAME, RETRIEVE_NUM

config = configparser.ConfigParser()
config.read('../config.ini')

redis_client = get_redis_connection()

# openai.api_key = config['OPENAI']['API_KEY']

# A basic class to create a message as a dict for chat
class Message:
    
    def __init__(self, role,content):
        self.role = role
        self.content = content
        
    def message(self):
        return {
            "role": self.role,
            "content": self.content
        }


# New Assistant class to add a vector database call to its responses
class RetrievalAssistant:
    
    def __init__(self):
        self.conversation_history = []  

    def _get_assistant_response(self, prompt):
        try:
            completion = openai.ChatCompletion.create(
              model=CHAT_MODEL,
              messages=prompt,
              temperature=0.1
            )
            logging.info(f"Sent prompt: {prompt}")
            
            response_message = Message(
                completion['choices'][0]['message']['role'],
                completion['choices'][0]['message']['content']
            )
            return response_message.message()
            
        except Exception as e:

            return f'Request failed with exception {e}'
    
    # The function to retrieve Redis search results

    def _get_search_results(self,prompt):
        latest_question = prompt
        search_content = get_redis_results(
            redis_client,latest_question, 
            INDEX_NAME
        )['result'][0:RETRIEVE_NUM]
        response = ''
        for r in search_content:
            response += r
            #logging.info(r)

        return response
        
    def ask_assistant(self, next_user_prompt):
        [self.conversation_history.append(x) for x in next_user_prompt]
        assistant_response = self._get_assistant_response(self.conversation_history)
        
        # Answer normally unless the trigger sequence is used "searching_for_answers"
        if 'searching for answers' in assistant_response['content'].lower():
            logging.info('Searching from database...')
            question_extract = openai.Completion.create(
                model = COMPLETIONS_MODEL, 
                prompt=f'''
                Extract the user's latest question for that question from this 
                conversation: {self.conversation_history}. Extract it as a sentence stating the Question"
            '''
            )
            search_result = self._get_search_results(question_extract['choices'][0]['text'])
            logging.info(f'Search result:{search_result}')
            
            # We insert an extra system prompt here to give fresh context to the Chatbot on how to use the Redis results
            # In this instance we add it to the conversation history, but in production it may be better to hide
            self.conversation_history.insert(
                -1, {
                "role": 'system',
                "content": f'''
                Answer the user's last question using this content: {search_result}. 
                If you cannot answer the question, say 'Sorry, I don't know the answer to this one'

                Answer:
                '''
                }
            )
            
            assistant_response = self._get_assistant_response(
                self.conversation_history
                )
            
            self.conversation_history.append(assistant_response)
            logging.info(f"Summary: {assistant_response}")
            return assistant_response
        else:
            self.conversation_history.append(assistant_response)
            return assistant_response
            
    def pretty_print_conversation_history(
            self, 
            colorize_assistant_replies=True):
        
        for entry in self.conversation_history:
            if entry['role']=='system':
                pass
            else:
                prefix = entry['role']
                content = entry['content']
                if colorize_assistant_replies and entry['role'] == 'assistant':
                    output = colored(f"{prefix}:\n{content}, green")
                else:
                    output = colored(f"{prefix}:\n{content}")
                print(output)


class IncubationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        self.tools = [
            Tool(
                name="HKSTP-Incubation-DB",
                func=self._get_search_results,
                description="useful for when you need to answer questions about Incubation of HKSTP. Input should be in the form of a question containing full context"
            )
        ]
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = initialize_agent(self.tools, self.llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory = self.memory)

    def _get_search_results(self, prompt: str) -> str:
        latest_question = prompt
        search_content = get_redis_results(
            redis_client,latest_question, 
            INDEX_NAME
        )['result'][0:RETRIEVE_NUM]
        response = ''
        for r in search_content:
            response += r
            #logging.info(r)

        return response
    
    def ask_assistant(self, prompt):
        rsps = self.agent.run(prompt)
        return rsps
import streamlit as st
from streamlit_chat import message

from database import get_redis_connection
from chatbot import RetrievalAssistant, Message

import configparser

# Initialise database

## Initialise Redis connection
config = configparser.ConfigParser()
config.read('../config.ini')

redis_client = get_redis_connection()

# Set instruction

# System prompt requiring Question and Year to be extracted from the user
system_prompt = '''
You are a helpful HKSTP based knowledge base assistant. You need to capture the Question of each customer.
The Question is their query on HKSTP.
Think about this step by step:
- The user will ask a Question about HKSTP
- Once you have the Question, you can answer "Searching for answers.", which will trigger a retrieval so that you can get some information to sum up
- After retrieving some result, the system will send you the information to answer user's question
- If you are asked a daily question, you can directly answer

Example 1:

User: I'd like to know the admission criteria for HKSTP Incubation program

Assistant: Certainly, Searching for answers.

System: Answer the user's last question using this content: *some search_result*

Assistant: * Summary of the result for the question*

Example 2:
User: How's everything going

Assistant: Everything alright! What about you?
'''

### CHATBOT APP

st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

st.title('HKSTP Chatbot')
st.subheader("Help us help you learn about HKSTP")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def query(question):
    response = st.session_state['chat'].ask_assistant(question)
    return response

prompt = st.text_input(f"What do you want to know: ", key="input")

if st.button('Submit', key='generationSubmit'):

    # Initialization
    if 'chat' not in st.session_state:
        st.session_state['chat'] = RetrievalAssistant()
        messages = []
        system_message = Message('system',system_prompt)
        messages.append(system_message.message())
    else:
        messages = []


    user_message = Message('user',prompt)
    messages.append(user_message.message())

    response = query(messages)

    # Debugging step to print the whole response
    #st.write(response)

    st.session_state.past.append(prompt)
    st.session_state.generated.append(response['content'])

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

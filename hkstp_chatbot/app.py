from flask import Flask, request, jsonify, render_template, session, Response, copy_current_request_context
import threading
import queue
import pickle
from database import get_redis_connection
from chatbot import RetrievalAssistant, Message, IncubationAgent, ThreadedGenerator
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

app = Flask(__name__)

class Config(object):
    SECRET_KEY = "DJFAJLAJAFKLJQ"

@app.route('/')
def index():
    init_text = "Hi, I am HKSTP incubation program AI assistant."
    bubbles = [
        {
            'id': 1,
            'text': f'{init_text}',
            'fromChatbot': True
        }
    ]
    session['chat'] = IncubationAgent().extract_memory()
    return render_template('chat.html')

def agent_thread(g, agent, prompt, commu_dict):
    try:
        # reload llm inside agent with thread generator
        agent.reload_llm(callback_generator = g)
        response = agent.ask_assistant(prompt)
        logging.info(response)
    finally:
        commu_dict['chat'] = agent.extract_memory()
        logging.info(f"message dicts in thread: {agent.extract_memory()}")
        g.close()

def chain(agent, prompt, commu_dict):
    g = ThreadedGenerator()
    threading.Thread(target=agent_thread, args=(g, agent, prompt, commu_dict)).start()
    return g

@app.route('/submit', methods=['POST'])
def submit():
    
    data = request.get_json()
    text = data['text']
    agent = IncubationAgent()
    commu_dict = {'chat': []}
    if 'chat' in session:
        logging.info("session chat exits")
        chat_messages = session['chat']
        logging.info(f"chat_messages in session: {chat_messages}")
    agent.load_memory(session['chat'])
    logging.info(text)

    response = Response(chain(agent = agent, prompt = text, commu_dict = commu_dict), mimetype='text/plain')
    @response.call_on_close
    def _on_close():
        logging.info("Response done")
        session['chat'] = commu_dict['chat']
        logging.info(f"session message dicts: {session['chat']}")

    return response

if __name__ == '__main__':
    app.config.from_object(Config())
    app.run(host = '0.0.0.0', debug=True, threaded = True)
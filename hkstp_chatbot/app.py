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
    return render_template('chat.html')

def agent_thread(g, agent, prompt, memory):
    try:
        # reload llm inside agent with thread generator
        agent.reload_llm(callback_generator = g, memory = memory)
        response = agent.ask_assistant(prompt)
        logging.info(response)
    finally:
        g.close()

def chain(agent, prompt, memory):
    g = ThreadedGenerator()
    threading.Thread(target=agent_thread, args=(g, agent, prompt, memory)).start()
    return g

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    text = data['text']
    if 'chat' not in session:
        session_memory = IncubationAgent().memory
        session['chat'] = pickle.dumps(session_memory)
    agent = IncubationAgent()
    session_memory = pickle.loads(session['chat'])
    logging.info(text)
    try:
        return Response(chain(agent = agent, prompt = text, memory = session_memory), mimetype='text/plain')
    finally:
        logging.info("Response done")
        session['chat'] = pickle.dumps(agent.memory)

if __name__ == '__main__':
    app.config.from_object(Config())
    app.run(host = '0.0.0.0', debug=True, threaded = True)
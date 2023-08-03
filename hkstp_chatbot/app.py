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

@copy_current_request_context
def agent_thread(g, agent, prompt):
    try:
        agent.ask_assistant(prompt)
    finally:
        g.close()
        session['chat'] = pickle.dumps(agent)


def chain(agent, prompt):
    g = ThreadedGenerator()
    threading.Thread(target=agent_thread, args=(g, agent, prompt)).start()
    return g

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    text = data['text']
    if 'chat' not in session:
        session['chat'] = pickle.dumps(IncubationAgent())
    agent = pickle.loads(session['chat'])
    # response = agent.ask_assistant(text)
    # session['chat'] = pickle.dumps(agent)
    # logging.info(response)
    return Response(chain(agent = agent, prompt = text), mimetype='text/plain')

if __name__ == '__main__':
    app.config.from_object(Config())
    app.run(host = '0.0.0.0', debug=True, threaded = True)
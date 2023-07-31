from flask import Flask, request, jsonify, render_template, session
import pickle
from database import get_redis_connection
from chatbot import RetrievalAssistant, Message, IncubationAgent

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

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    text = data['text']
    if 'chat' not in session:
        session['chat'] = pickle.dumps(IncubationAgent())
    agent = pickle.loads(session['chat'])
    response = agent.ask_assistant(text)
    session['chat'] = pickle.dumps(agent)

    return jsonify(response)

if __name__ == '__main__':
    app.config.from_object(Config())
    app.run(host = '0.0.0.0', debug=True)
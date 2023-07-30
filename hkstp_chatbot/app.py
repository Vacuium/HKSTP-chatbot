from flask import Flask, request, jsonify, render_template, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

# from database import get_redis_connection
# from chatbot import RetrievalAssistant, Message, IncubationAgent


UPLOAD_FOLDER = r'.\UPLOAD_FILE'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

class Config(object):
    SECRET_KEY = "DJFAJLAJAFKLJQ"
    UPLOAD_FOLDER = UPLOAD_FOLDER

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
    # if 'chat' not in session:
    #     session['chat'] = IncubationAgent()

    # response = session['chat'].ask_assistant(text)

    # return jsonify({'response': response})
    return text

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        logging.info(type(file))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200

if __name__ == '__main__':
    app.config.from_object(Config())
    app.run(host = '0.0.0.0', debug=True)
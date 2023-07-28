FROM hkstpchatbot

WORKDIR ./app

COPY . .

# RUN pip install pip update
# RUN pip3 install -r requirements.txt

EXPOSE 8501

CMD ["streamlit","run", "./hkstp_chatbot/chat.py"]
# CMD ["python3", "./vecdbsetting.py"]
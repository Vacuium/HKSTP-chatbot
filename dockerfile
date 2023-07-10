FROM python:3.11


WORKDIR ./app

COPY . .

RUN pip install pip update
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["streamlit", "run", "./hkstp_chatbot/chat.py"]
FROM python:3.10

WORKDIR ./app

COPY . .

RUN pip install pip update
RUN pip3 install -r requirements.txt
# RUN cd ./hkstp_chatbot

EXPOSE 5000

CMD ["streamlit","run", "./hkstp_chatbot/app.py"]
# CMD ["python3", "./vecdbsetting.py"]
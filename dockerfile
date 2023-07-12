FROM python:3.11


WORKDIR ./app

COPY . .

RUN pip install pip update
RUN pip3 install -r requirements.txt
RUN cd ./hkstp_chatbot

EXPOSE 8501

CMD ["streamlit", "run", "./chat.py"]
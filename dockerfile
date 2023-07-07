FROM python:3.11


WORKDIR ./app

COPY hkstp_chatbot hkstp_chatbot
COPY vecdbsetting.py vecdbsetting.py
COPY data data
COPY requirements.txt requirements.txt
COPY config.ini config.ini

RUN pip install pip update
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "./vecdbsetting.py"]
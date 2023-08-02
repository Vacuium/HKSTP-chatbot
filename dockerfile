FROM python:3.10

WORKDIR ./app

COPY . .

RUN pip install pip update
RUN pip3 install -r requirements.txt

EXPOSE 5000

# CMD ["python", "./hkstp_chatbot/app.py"]
CMD ["python3", "./vecdbsetting.py"]

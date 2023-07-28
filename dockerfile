FROM hkstpchatbot

WORKDIR ./app

COPY . .

RUN pip install pip update
RUN pip3 install -r requirements.txt
# RUN cd ./hkstp_chatbot

EXPOSE 5000

CMD ["flask","run", "./hkstp_chatbot/app.py"]
# CMD ["python3", "./vecdbsetting.py"]

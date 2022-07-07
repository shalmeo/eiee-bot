FROM python:3.10-slim

WORKDIR /usr/src/app/eiee-bot

COPY requirements.txt /usr/src/app/eiee-bot
RUN pip install -r /usr/src/app/eiee-bot/requirements.txt
COPY . /usr/src/app/eiee-bot

CMD python -m app
FROM python:3.10-slim

ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app/"${BOT_NAME}-bot"

COPY requirements.txt /usr/src/app/"${BOT_NAME}-bot"
RUN pip install -r /usr/src/app/"${BOT_NAME}-bot"/requirements.txt
COPY . /usr/src/app/"${BOT_NAME}-bot"

CMD python -m app
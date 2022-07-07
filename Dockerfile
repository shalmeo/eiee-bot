FROM python:3.10-slim

WORKDIR /usr/src/app/eiee-bot

COPY requirements.txt /usr/src/app/eiee-bot
RUN apt-get update \
 && apt-get install -y gcc \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt \
 && rm -rf /var/lib/apt/lists/*
COPY . /usr/src/app/eiee-bot

CMD python -m app

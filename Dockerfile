FROM python:3.11-slim

WORKDIR /level-up

COPY requirements.txt .
COPY levelup/*.py levelup/.

RUN pip install -r requirements.txt
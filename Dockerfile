FROM python:3.11-slim

WORKDIR /level-up

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY tdd.py tdd.py
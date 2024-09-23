FROM python:3.11-slim

WORKDIR /level-up

COPY requirements.txt .
COPY levelup/*.py levelup/.

RUN pip install -r requirements.txt

ENV OPENAI_API_MODEL="gpt-4o-mini"

CMD ["/bin/sh","-c","\"while sleep 1000; do :; done\""]
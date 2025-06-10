FROM python:3.12-slim

WORKDIR /assured-tdd

RUN apt-get update && \
    apt-get upgrade -y

COPY requirements.txt .
COPY tdd/*.py tdd/.
COPY *.py .

RUN pip install -r requirements.txt

CMD ["/bin/sh","-c","while sleep 1000; do :; done"]
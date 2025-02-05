FROM python:3.11-slim

WORKDIR /levelup

RUN apt-get update && \
    apt-get upgrade -y

COPY requirements.txt .
COPY levelup/*.py levelup/.

RUN pip install -r requirements.txt

CMD ["/bin/sh","-c","while sleep 1000; do :; done"]
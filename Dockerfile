FROM python:3.11-slim

WORKDIR /level-up

COPY requirements.txt .
COPY levelup/*.py levelup/.

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git
RUN metagpt --init-config

COPY config2.yaml /root/.metagpt/.

CMD ["/bin/sh","-c","while sleep 1000; do :; done"]
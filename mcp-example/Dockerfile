FROM python:3.12-slim

WORKDIR /mcp-example

RUN apt-get update && \
    apt-get upgrade -y  && \
    apt-get install -y git

RUN git clone https://github.com/rjust/defects4j.git

COPY client.py .
COPY mcp-git-server.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["/bin/sh","-c","while sleep 1000; do :; done"]



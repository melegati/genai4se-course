FROM quay.io/jupyter/base-notebook:python-3.12

WORKDIR /home/jovyan/work

USER root

RUN apt-get update && \
    apt-get upgrade -y  

USER $NB_UID

COPY opendatahub.json .
COPY RAGforAPI.ipynb .

EXPOSE 8888

CMD ["start-notebook.sh"]
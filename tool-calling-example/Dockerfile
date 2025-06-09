FROM quay.io/jupyter/base-notebook:python-3.12

USER root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git    

USER $NB_UID

WORKDIR /home/jovyan/work

COPY FunctionCallingForGit.ipynb .

EXPOSE 8888

CMD ["start-notebook.sh"]
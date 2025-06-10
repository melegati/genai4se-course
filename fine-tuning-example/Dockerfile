# Use the official Jupyter base image
FROM quay.io/jupyter/base-notebook:python-3.12

# Set the working directory
WORKDIR /home/jovyan/work

USER root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install unzip

USER $NB_UID

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your notebook into the image (replace with your actual filename)
COPY VulnerabilityDetection.ipynb .

# Expose the Jupyter port
EXPOSE 8888

# Automatically start Jupyter Notebook
CMD ["start-notebook.sh"]

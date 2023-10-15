FROM apache/airflow:2.7.0
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
  
# Install Chrome and setup Driver
# Update package lists and install wget
RUN apt-get update && apt-get install -y wget

# Download Google Chrome .deb file and copy it to /tmp
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /tmp/

# Install necessary dependencies and Google Chrome
RUN apt-get update && \
    apt-get install -y wget && \
    dpkg -i /tmp/google-chrome-stable_current_amd64.deb || apt-get -f install -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm /tmp/google-chrome-stable_current_amd64.deb

USER airflow

COPY airflow-requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /airflow-requirements.txt
# Extend the Airflow image
FROM apache/airflow:2.9.3



# Install additional dependencies
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean


COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

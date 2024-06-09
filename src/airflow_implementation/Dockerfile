FROM apache/airflow:2.9.0

USER root

COPY /python_envs/webscraping_venv_requirements.txt /opt/airflow/python_envs/webscraping_venv_requirements.txt

RUN apt-get update && apt-get -y install libpq-dev gcc 

# Building the necessary python Venvs that are used to run dags:
RUN python -m venv /opt/airflow/python_envs/webscraping_venv \
    && /opt/airflow/python_envs/webscraping_venv/bin/python -m pip install -r /opt/airflow/python_envs/webscraping_venv_requirements.txt

# Installing the JDK to run my .jar files:
RUN apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow
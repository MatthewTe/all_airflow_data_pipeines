FROM apache/airflow:2.9.0

USER root

COPY /python_envs/webscraping_venv_requirements.txt /opt/airflow/python_envs/webscraping_venv_requirements.txt

RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN python -m venv /opt/airflow/python_envs/webscraping_venv \
    && /opt/airflow/python_envs/webscraping_venv/bin/python -m pip install -r /opt/airflow/python_envs/webscraping_venv_requirements.txt

USER airflow
import sys
from datetime import datetime, timedelta
from datetime import datetime

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.decorators import task
from airflow.models import Variable

with DAG(
    "extracting_combat_footage_subreddit_metadata",
    description='DAG that runs the jar of the subreddit metadata ingestor that writes the data to the databasthe subreddit metadata ingestor that writes subreddit post metadata to the db',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['reddit', 'combat_footage', 'metadata', 'subreddit']
) as dag:

    @task.bash
    def run_subreddit_ingestion_task() -> str:
        return "echo Hello World"

    run_subreddit_ingestion_task()
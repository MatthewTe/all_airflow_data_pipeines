import sys
from datetime import datetime, timedelta
from datetime import datetime

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.decorators import task
from airflow.models import Variable

with DAG(
    "extracting_looptt_crime_articles",
    description='DAG that makes a request to the Loop TT news website to extract all of the crime news',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['crime', 'Trinidad']
) as dag:



    @task.external_python(python="/opt/airflow/python_envs/webscraping_venv/bin/python")
    def run_extract_loop_crime(query_param_str: str ,  db_url: str):
        
        sys.path.append('/opt/airflow/dags/library')
        from library.webscraping.news_extraction import process_loop_page, LoopPageConfig

        config: LoopPageConfig = {
            "query_param_str": query_param_str,
            "article_category": "looptt-crime",
            'db_category': "crime",
            'db_url':db_url
        }

        process_loop_page(config=config)
    
    external_python_task = run_extract_loop_crime(
        query_param_str='?page=0', 
        db_url=Variable.get('main_db_str')
    )

with DAG(
    "extracting_looptt_politics_articles",
    description='DAG that makes a request to the Loop TT news website to extract all of the politics articles',
    schedule=timedelta(days=2),
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['Trinidad', 'politics']
) as politics_dag:
    pass

    @task.external_python(python="/opt/airflow/python_envs/webscraping_venv/bin/python")
    def run_extract_loop_politics(query_param_str: str ,  db_url: str):
        
        sys.path.append('/opt/airflow/dags/library')
        from library.webscraping.news_extraction import process_loop_page, LoopPageConfig

        config: LoopPageConfig = {
            "query_param_str": query_param_str,
            "article_category": "looptt-politics",
            'db_category': "politics",
            'db_url':db_url
        }

        process_loop_page(config=config)
    
    external_python_task = run_extract_loop_politics(
        query_param_str='?page=0', 
        db_url=Variable.get('main_db_str')
    )

with DAG(
    "extracting_looptt_caribbean_news",
    description='DAG that makes a request to the Loop TT news website to extract all of the caribbean news articles',
    schedule=timedelta(days=2),
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['Trinidad', 'news', 'caribbean']
) as caribbean_news_dag:
    pass

    @task.external_python(python="/opt/airflow/python_envs/webscraping_venv/bin/python")
    def run_extract_loop_caribbean_news(query_param_str: str ,  db_url: str):
        
        sys.path.append('/opt/airflow/dags/library')
        from library.webscraping.news_extraction import process_loop_page, LoopPageConfig

        config: LoopPageConfig = {
            "query_param_str": query_param_str,
            "article_category": "looptt-caribbean-news",
            'db_category': "caribbean-news",
            'db_url':db_url
        }

        process_loop_page(config=config)
    
    external_python_task = run_extract_loop_caribbean_news(
        query_param_str='?page=0', 
        db_url=Variable.get('main_db_str')
    )

if __name__ == "__main__":
    dag.test()
    politics_dag.test()
    caribbean_news_dag.test()

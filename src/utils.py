import sqlalchemy as sa
import dotenv
import os
import pandas as pd
import sqlite3

dotenv.load_dotenv('./airflow_implementation/.env')


def migrate_sqlite_to_psql():
    DB_USER = os.environ.get('POSTGRES_USER')
    DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD').encode('utf-8').decode('utf-8')
    DB_NAME = os.environ.get('POSTGRES_DB')

    db_uri = r"postgresql+psycopg2://{0}:{1}@10.0.0.85/{2}".format(
        DB_USER, DB_PASSWORD, DB_NAME
    )

    POSTGRES_Engine: sa.engine.Engine = sa.create_engine(db_uri)

    SQLITE_Engine: sa.engine.Engine = sa.create_engine("sqlite:////Users/matthewteelucksingh/Repos/TT_info_classifier/data/dev_db.sqlite3")

    conn = sqlite3.connect("/Users/matthewteelucksingh/Repos/TT_info_classifier/data/dev_db.sqlite3")
    with conn:
        df = pd.read_sql(sql="SELECT * FROM articles", con=conn)

    print(df)

    with POSTGRES_Engine.connect() as conn, conn.begin():
        df.to_sql('articles', con=conn, if_exists='append', index=False)

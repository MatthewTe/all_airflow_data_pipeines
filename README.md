# All airflow data pipelines
Containing all of the pipelines and libraries for running all of my data ingestion pipelines.


```
Database Backup commands:
python backup_db.py directory password server_ip_address

pg_dump -U tt_ingest -h {host} -p 5432 -F t {database} -f {database_backup_tar_file}
```
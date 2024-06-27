import subprocess
import os
import sys
import pathlib
import datetime

DATABASE_NAMES = ['tt_data', 'articles_dev', 'articles_prod']
DOCKER_VOLUME_PATHS = {
    "airflow_postgres_volume": "/var/lib/docker/volumes/airflow_implementation_postgres-db-volume/_data",
    "database_postgres_volume":"/var/lib/docker/volumes/airflow_implementation_postgres-main-db-volume/_data",
    "minio_static_data":"/var/lib/docker/volumes/airflow_implementation_minio_data/_data"
}

if __name__ == '__main__':

    backup_directory, database_pwrd, host, host_pwd  = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]

    # Database table direct backups:
    for database in DATABASE_NAMES:

        database_backup_dir: pathlib.Path = backup_directory / "databases"
        database_backup_dir: pathlib.Path = database_backup_dir / database
        database_backup_dir.mkdir(parents=True, exist_ok=True)
        
        current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%Y")
        database_backup_tar_file = database_backup_dir / f"{database}_backup_{current_time}.tar"

        backup_cmd = f"pg_dump -U tt_ingest -h {host} -p 5432 -F t {database} -f {database_backup_tar_file}"
        env = os.environ.copy()
        env['PGPASSWORD'] = database_pwrd

        try:
            r = subprocess.run(backup_cmd, env=env, check=True, shell=True)
            print(f"Backup for database {database} completed successfully archived in following location {database_backup_tar_file}")       
        except subprocess.CalledProcessError as e:
            print(f"Error occured while backing p database {database}: {str(e.with_traceback(None))}")
    
    # Backing up the docker volumn snapshots:
    for name, volume_path in DOCKER_VOLUME_PATHS.items():

        print(f"Beginning backing up volume: {name}")
        volume_backup_dir = pathlib.Path = backup_directory / "volumes"
        volume_backup_dir = volume_backup_dir / name
        volume_backup_dir.mkdir(parents=True, exist_ok=True)

        current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%Y")
        tar_filename = volume_backup_dir / f"volume_backup_{current_time}.tar.gz"

        tar_scp_cmd = (
        f"sshpass -p '{host_pwd}' ssh matthew@{host} "
        f"'echo {host_pwd} | sudo -S tar -czf - -C {volume_path} .' | "
        f"cat > {tar_filename}"
    )
        try:
            r = subprocess.run(tar_scp_cmd, check=True, shell=True)
            print(f"Backup for volume {name} completed successfully at location {tar_filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error occured while backing up volume {name}: {str(e.with_traceback(None))}")

    sys.exit(0)

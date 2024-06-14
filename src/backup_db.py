import subprocess
import os
import sys
import pathlib
import datetime

DATABASE_NAMES = ['tt_data', 'articles_dev', 'articles_prod']

if __name__ == '__main__':

    backup_directory, database_pwrd, host = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]

    for database in DATABASE_NAMES:

        database_backup_dir: pathlib.Path = backup_directory / database
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

    sys.exit(0)

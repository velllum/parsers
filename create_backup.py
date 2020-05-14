import requests
import os
import time

ROOT_SERVER_PATH = '/home/v/name_login'
URL_DOWNLOAD_MYSQL_BACKUP = 'https://api.beget.com/api/backup/downloadMysql?login=name_login&passwd=password&input_format=json&output_format=json&input_data={"backup_id":"","bases":["name_base"]}'
URL_LOG_ALL_BACKUP = 'https://api.beget.com/api/backup/getLog?login=name_login&passwd=password&output_format=json'

def create_sql_backup():
    return requests.get(URL_DOWNLOAD_MYSQL_BACKUP).json()

def get_log_backup():
    return requests.get(URL_LOG_ALL_BACKUP).json()['answer']['result']

def remove_file(file_path):
    os.remove(file_path)



def main():
    backup = create_sql_backup()
    print(backup)

    if backup:

        time.sleep(10)

        res = [r for r in get_log_backup() if r['type'] == 'download_mysql']

        rem_file = f"_live.{res[2]['target_list'][0]}.{res[2]['id']}.sql.gz"

        files = os.listdir(ROOT_SERVER_PATH)

        if rem_file in files:
            remove_file(file_path=f'{ROOT_SERVER_PATH}/{rem_file}')

        return True

    return False


if __name__ == '__main__':
    main()
    
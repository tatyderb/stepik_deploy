import logging

import pyaml_env
from pathlib import Path

from src.logged_requests import LOGGER_NAME


API_HOST = 'https://stepik.org'
CLIENT_ID = "..."
CLIENT_SECRET = "..."
AUTH_FILENAME = 'auth.yaml'

logger = logging.getLogger(LOGGER_NAME)


def get_creds():
    return CLIENT_ID, CLIENT_SECRET


def ask_and_write_auth(path):
    """Запрашивает у пользователя креды и записывает их в файл path"""
    global CLIENT_ID
    global CLIENT_SECRET
    print('Wrong client credentials.')
    print('Go to https://stepik.org/oauth2/applications/, get authorisation data.')
    print('For stepik: Сlient type = confidential, Authorization Grant Type = client-credentials.')
    CLIENT_ID = input('CLIENT_ID : ').strip()
    CLIENT_SECRET = input('CLIENT_SECRET : ').strip()
    with open(path, 'w', encoding='utf8') as fout:
        print(f'CLIENT_ID: {CLIENT_ID}', file=fout)
        print(f'CLIENT_SECRET: {CLIENT_SECRET}', file=fout)
    print(f'Credentials have been saved in {path}')
    print('You may store creds as environment variables. See more info in https://github.com/mkaranasou/pyaml_env')


def read_or_create_auth_data():
    """Читает креды из auth.yaml, если файла нет или креды пустые, запрашивает креды и сохраняет в файл ./auth.yaml"""
    global CLIENT_ID
    global CLIENT_SECRET
    filename = Path(__file__).resolve().parent / AUTH_FILENAME
    print(filename)
    # файла нет? пишем креды
    if not filename.exists():
        print(f'No file {filename}')
        ask_and_write_auth(path=filename)

    # креды отсутствуют? просим пользователя их ввести
    while True:
        creds = pyaml_env.parse_config(str(filename))
        CLIENT_ID = creds.get('CLIENT_ID')
        CLIENT_SECRET = creds.get('CLIENT_SECRET')
        logger.info(f'{CLIENT_ID=}, {CLIENT_SECRET=}')
        if CLIENT_ID and CLIENT_SECRET:
            break
        ask_and_write_auth(path=filename)

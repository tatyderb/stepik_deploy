"""
API for add, update or delete Stepik objects: steps.
"""
import logging

import requests
from src.auth import API_HOST, get_creds #CLIENT_ID, CLIENT_SECRET
from src.logged_requests import LoggedSession, LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class Session(LoggedSession):
    def __init__(self):
        # TODO: параметры конфигурации брать не дефолтные, а из конфигурационного файла
        super().__init__({})
        client_id, client_secret = get_creds()
        logger.info(f'{client_id=}, {client_secret=}')
        self.token = self.get_token(client_id, client_secret)

    def get_token(self, client_id, client_secret):
        logger.info(f'{client_id=}, {client_secret=}')
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        logger.info(f'{auth=}')
        response = self.request('POST', f'{API_HOST}/oauth2/token/', data={'grant_type': 'client_credentials'},
                                 auth=auth)
        # print(response)
        # status code should be 200 (HTTP OK)
        assert (response.status_code == 200)
        token = response.json()['access_token']
        logger.info(f'TOKEN = {token}')
        return token

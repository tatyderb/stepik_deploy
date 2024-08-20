"""
API for add, update or delete Stepik objects: steps.
"""
import json
import logging
import pprint
import requests
import sys
import traceback

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

    def update_object(self, object_name, object_id, data: dict):
        """Update object_name = 'lesson'|'step'|etc, object_id - ID. """
        api_url = f'{API_HOST}/api/{object_name}/{object_id}'
        # use PUT to update existing objects
        response = self.request('PUT', api_url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
        # status code should be 200 (HTTP OK)
        try:
            assert (response.status_code == 200)
        except AssertionError as e:
            traceback.print_exc()
            print(response.status_code)
            pprint.pprint(response.content)
            pprint.pprint(json.dumps(json.loads(response.content), indent=4))
            sys.exit(1)

        object_id = response.json()[object_name][0]['id']
        return object_id

    # 3. Call API (https://stepik.org/api/docs/) using this token.
    def fetch_object(self, obj_class, obj_id):
        api_url = f'{API_HOST}/api/{obj_class}s/{obj_id}'
        response = self.request('GET', api_url,
                                headers={'Authorization': 'Bearer ' + self.token}).json()
        return response[f'{obj_class}s'][0]

    def fetch_objects(self, obj_class, obj_ids, keep_order=True):
        objs = []
        # Fetch objects by 30 items,
        # so we won't bump into HTTP request length limits
        step_size = 30
        for i in range(0, len(obj_ids), step_size):
            obj_ids_slice = obj_ids[i:i + step_size]
            params = '&'.join(['ids[]={obj_id}' for obj_id in obj_ids_slice])
            api_url = f'{API_HOST}/api/{obj_class}s?' + params
            response = self.request('GET', api_url,
                                    headers={'Authorization': 'Bearer ' + self.token}
                                    ).json()

            objs += response[f'{obj_class}s']
        if keep_order:
            return sorted(objs, key=lambda x: obj_ids.index(x['id']))
        return objs

    def create_object(self, object_name, data: dict):
        api_url = f'{API_HOST}/api/{object_name}'
        # use POST to create_by_type new objects
        response = self.request('POST', api_url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
        # status code should be 201 (HTTP Created)
        assert (response.status_code == 201)
        object_id = response.json()[object_name][0]['id']
        return object_id

    def delete_object(self, object_name: str, object_id: int):
        api_url = f'{API_HOST}/api/{object_name}/{object_id}'
        response = self.request('DELETE', api_url, headers={'Authorization': 'Bearer ' + self.token})
        # status code should be 204 (HTTP Created)
        # print(response.status_code)
        assert (response.status_code == 204)

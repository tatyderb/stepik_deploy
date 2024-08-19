from src.auth import read_or_create_auth_data

from src.stepik_api import Session


def test_get_token():
    read_or_create_auth_data()
    session = Session()


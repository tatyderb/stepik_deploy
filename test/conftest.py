import logging
import pytest

from src import logged_requests
from src.auth import read_or_create_auth_data

logger = None


@pytest.fixture(scope='session', autouse=True)
# def log_test_stdout(env):
def setup_logger():
    # configure own logger before tests
    logged_requests.setup_logger(
        log_cli_level=logging.INFO,
        log_file_level=logging.INFO)

    global logger
    logger = logging.getLogger(logged_requests.LOGGER_NAME)
    logger.info('Start logger')


@pytest.fixture(scope='module')
def auth():
    read_or_create_auth_data()
    # просто заглушка, ибо нужно дернуть именно зачитывание кредов из конфигурационного файла
    return True

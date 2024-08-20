"""
Wrapper for requests.Session get/post/patch/
"""

import inspect
import json
import logging
import pathlib
import requests

# оставляем None, чтобы если мы не сконфигурировали логгер, а уже используем сессию, получилась ошибка.
LOGGER_NAME = 'stepik'
logger: logging.Logger = None       # setuped logger


def setup_logger(log_cli_level, log_file_level):
    """
    Use own logger for logging into out.log file and console(?)
    """
    global logger
    # print(f"Setup LOG LEVEL CLI={log_cli_level}, FILE={log_file_level}")
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(max(log_cli_level, log_file_level))

    # create_by_type file handler which logs even debug messages

    current = pathlib.Path(__file__).parent.parent.resolve()
    full_filename = str(current.joinpath('out.log'))

    fh = logging.FileHandler(full_filename, mode='w', encoding='utf-8')
    fh.setLevel(log_file_level)

    # create_by_type console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_cli_level)

    # create_by_type formatter and add it to the handlers
    formatter_full = logging.Formatter(
        '%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )
    formatter_short = logging.Formatter(
        '%(levelname)8s: %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )
    # formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter_full)
    # ch.setFormatter(formatter_short)

    # add the handlers to the logger
    # logger.addHandler(ch)
    logger.addHandler(fh)


class LoggedSession:
    """Обертка для requeists.Session с логированием запросов и ответов."""

    def __init__(self, cfg: dict):
        """ requests.Session with request/response dump,
        kwargs - environment config dict
        """
        self.__session = requests.Session()

        # что именно логировать в запросе и ответе
        self.log_url = True
        self.log_header = True
        self.log_data = True
        self.log_http_code = True
        self.log_resp_data = True

        # игнорировать ошибки ssl сертификата
        self.ignore_ssl_certificate_errors = False

        self.configure(cfg)

    def set_log_level_settings(self, env_loglevel: dict):
        if 'log_request_url' in env_loglevel:
            self.log_url = env_loglevel['log_request_url']
        if 'log_request_header' in env_loglevel:
            self.log_header = env_loglevel['log_request_header']
        if 'log_request_body' in env_loglevel:
            self.log_data = env_loglevel['log_request_body']
        if 'log_response_http_code' in env_loglevel:
            self.log_http_code = env_loglevel['log_response_http_code']
        if 'log_response_data' in env_loglevel:
            self.log_resp_data = env_loglevel['log_response_data']

    def configure(self, cfg: dict):
        if 'log' in cfg:
            self.set_log_level_settings(cfg['log'])
        # self.ignore_ssl_certificate_errors = cfg['ignore_ssl_certificate_errors']

    def request(self, method, url, stacklevel=3, log_response_data=True, **kwargs):
        # stacklevel - up to stack call level: now, object_function, test_function
        # logger.info(f'{method} {url}')
        ''' old approach, since python 3.8 use stacklevel option
        called_function_info = inspect.stack()[1]
        extra = {
            'filename': called_function_info.filename,
            'lineno': called_function_info.lineno,
            'funcName': called_function_info.function
        }
        '''
        if self.log_url:
            logger.info(f'{method} {url}', stacklevel=stacklevel)
        if self.log_header:
            logger.info(f"Request Headers: {json.dumps(kwargs.get('headers', None))}", stacklevel=stacklevel)
            if kwargs.get('cookies'):
                logger.info(f"Request Cookies: {json.dumps(kwargs.get('cookies'))}", stacklevel=stacklevel)

        if self.log_data:
            if 'data' in kwargs:
                logger.info(f"data = {str(kwargs['data'])}", stacklevel=stacklevel)
            if 'json' in kwargs:
                logger.info(f"json = {json.dumps(kwargs['json'])}", stacklevel=stacklevel)

        # verify=False only for disable ssl certificate check in stage.
        res = self.__session.request(
            method=method,
            url=url,
            verify=not self.ignore_ssl_certificate_errors,
            **kwargs
        )
        if self.log_http_code:
            logger.info(f'Status Code: {res.status_code}', stacklevel=stacklevel)

        if res.status_code >= 400:
            logger.info(f"response.text = {res.text}", stacklevel=stacklevel)
        elif log_response_data:
            if not res.content or json.dumps(res.json()) is None:
                logger.info(f"response.text = {res.text}", stacklevel=stacklevel)
            else:
                logger.info(f"response.json = {json.dumps(res.json())}", stacklevel=stacklevel)

        logger.info('-' * 10, stacklevel=stacklevel)
        return res

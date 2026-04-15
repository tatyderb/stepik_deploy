import logging
import pytest

from src import logged_requests
from src.auth import read_or_create_auth_data
from src.settings import settings

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


@pytest.fixture(autouse=True)
def manage_step_begin(request):
    """
    Универсальная фикстура для управления settings.STEP_BEGIN

    Использование:
        - По умолчанию: STEP_BEGIN = "123"
        - Для конкретного теста: @pytest.mark.step_begin("456")
        - Для отключения: @pytest.mark.no_step_begin
        - Для всего модуля: @pytestmark = pytest.mark.step_begin("789")
    """
    # Проверяем нужно ли отключить фикстуру
    if 'no_step_begin' in request.keywords:
        yield
        return

    # Получаем желаемое значение из маркера
    marker = request.node.get_closest_marker('step_begin')
    value = marker.args[0] if marker else settings.LEGACY_STEP_BEGIN

    # Сохраняем и устанавливаем новое значение
    original_value = getattr(settings, 'STEP_BEGIN', None)
    settings.STEP_BEGIN = value

    yield

    # Восстанавливаем
    if original_value is not None:
        settings.STEP_BEGIN = original_value
    else:
        delattr(settings, 'STEP_BEGIN')

# Применение фикстуры manage_step_begin:
# # Применяется ко всем тестам в файле
# pytestmark = pytest.mark.step_begin("module_value")
#
# def test1():
#     assert settings.STEP_BEGIN == "module_value"
#
# @pytest.mark.step_begin("custom_value")
# def test2():
#     assert settings.STEP_BEGIN == "custom_value"
#
# @pytest.mark.no_step_begin
# def test3():
#     # settings.STEP_BEGIN не изменяется
#     pass
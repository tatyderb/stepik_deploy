import logging

import pytest

from src.logged_requests import LOGGER_NAME
from src.stepik_api import Session
from src.utils import current_md_hm


logger = logging.getLogger(LOGGER_NAME)


@pytest.fixture(scope='module')
def choice_body():
    date_str = current_md_hm()
    data = {
        'stepSource': {
            'block': {
                'name': 'choice',
                'text': f'Date: {date_str}',
                'source': {
                    'options': [
                        {'is_correct': False, 'text': '2+2=3', 'feedback': ''},
                        {'is_correct': True, 'text': '2+2=4', 'feedback': ''},
                        {'is_correct': False, 'text': '2+2=5', 'feedback': ''},
                    ],
                    'is_always_correct': False,
                    'is_html_enabled': True,
                    'sample_size': 3,
                    'is_multiple_choice': False,
                    'preserve_order': False,
                    'is_options_feedback': False
                }
            },
            'lesson': 0,
            'position': 3
        }
    }
    return data


def fill_body(body: dict, text: str, lesson_id: int, position: int = 0) -> dict:
    """Заполняет в копии body поля text, lesson_id, position (начиная с 1) и
    возвращает заполненную копию.
    """
    d = body.copy()
    d['stepSource']['block']['text'] = text
    d['stepSource']['lesson'] = lesson_id
    d['stepSource']['position'] = position
    return d


def test_get_token(auth):
    session = Session()
    # assert внутри, если дошли, то 200 ОК и токен вернули


def test_get_lesson_and_step(auth):
    """Получаем инфу об уроке (проверяем id и количество шагов) и о шаге (проверяем его id)"""
    # https://stepik.org/lesson/374339/step/1
    lesson_id = 374339

    session = Session()
    lesson_info = session.fetch_object('lesson', lesson_id)
    logger.info(lesson_info)
    assert lesson_info['id'] == lesson_id
    assert len(lesson_info['steps']) == 4

    step_id = lesson_info['steps'][-1]

    step_info = session.fetch_object('step', step_id)
    logger.info(step_info)
    assert step_info['id'] == step_id


def test_update_step(auth, choice_body):
    """ В уроке изменяем текст последнего шага, ставим временную метку.
    Проверяем, что в уроке не изменилось количество шагов и текст этого шага содержит метку.
    """
    # https://stepik.org/lesson/374339/step/1
    lesson_id = 374339

    date_str = f'Date: {current_md_hm()}'

    session = Session()
    lesson_info = session.fetch_object('lesson', lesson_id)
    step_ids = lesson_info['steps']
    step_id = step_ids[-1]

    # исправляем последний шаг
    body = fill_body(choice_body, text=date_str, lesson_id=lesson_id, position=len(step_ids))
    session.update_object('step-sources', step_id, body)

    # проверяем, что количество шагов не изменилось
    lesson_info = session.fetch_object('lesson', lesson_id)
    assert lesson_info['steps'] == step_ids

    # проверяем, что на последнем шаге стоит нужная временная метка
    step_info = session.fetch_object('step', step_id)
    logger.info(step_info)
    assert step_info['id'] == step_id
    assert step_info['block']['text'] == date_str


def test_create_delete_step(auth, choice_body):
    """ В урок добавляем шаг, проверяем, что в шаге наша метка времени, удаляем шаг."""
    # https://stepik.org/lesson/374339/step/1
    lesson_id = 374339

    date_str = f'Date: {current_md_hm()}'

    session = Session()
    lesson_info = session.fetch_object('lesson', lesson_id)
    step_ids_before = lesson_info['steps']
    steps_length_before = len(step_ids_before)

    # добавим последним шагом выбор с текстом date_str
    body = fill_body(choice_body, text=date_str, lesson_id=lesson_id, position=steps_length_before + 1)
    new_step_id = session.create_object('step-sources', body)

    # проверим, что добавилось именно так и именно туда
    lesson_info = session.fetch_object('lesson', lesson_id)
    logger.info(lesson_info)
    assert len(lesson_info['steps']) == steps_length_before + 1

    step_info = session.fetch_object('step', new_step_id)
    logger.info(step_info)
    assert step_info['id'] == new_step_id
    assert step_info['block']['text'] == date_str

    # удаляем добавленный шаг
    session.delete_object('step-sources', new_step_id)

    # проверяем, что удалился именно этот шаг
    lesson_info = session.fetch_object('lesson', lesson_id)
    logger.info(lesson_info)
    assert lesson_info['steps'] == step_ids_before







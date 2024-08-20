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
    logger.info = step_info
    assert step_info['id'] == step_id

def test_create_delete(auth, choice_body):
    """ В урок добавляем шаг, проверяем, что в шаге наша метка времени, удаляем шаг."""
    # https://stepik.org/lesson/374339/step/1
    lesson_id = 374339

    date_str = f'Date: {current_md_hm()}'

    session = Session()
    lesson_info = session.fetch_object('lesson', lesson_id)
    step_ids_before = lesson_info['steps']
    steps_length_before = len(step_ids_before)

    # добавим последним шагом выбор с текстом date_str
    body: dict = choice_body.copy()
    body['stepSource']['block']['text'] = date_str
    body['stepSource']['lesson'] = lesson_id
    body['stepSource']['position'] = steps_length_before + 1

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







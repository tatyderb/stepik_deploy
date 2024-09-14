"""Проверка функций-оберток над Stepik API в классах Step и Lesson."""
import pytest

from src.lesson import Lesson
from src.step import StepText
from src.stepik_api import Session
from src.utils import generate_timestring


# отлаживаемся на уроке https://stepik.org/lesson/1408550/step/1
# два текстовых шага
LESSON_ID = 1408550
STEP_IDS = [5845964, 5846066]


def generate_lesson_text_steps(step_number: int = 1) -> list[StepText]:
    """Возвращаем список из двух текстовых шагов с текущей датой."""
    # https://stepik.org/lesson/1408550/step/1?unit=1426036
    steps = [StepText(header=str(h)) for h in range(step_number)]
    time_str = generate_timestring()
    for i, s in enumerate(steps, 1):
        s.text = f'{i} {time_str}'
    return steps


def test_lesson_info(auth):
    """В уроке два шага."""
    session = Session()
    lesson = Lesson(lesson_id=LESSON_ID)
    lesson_info, step_ids = lesson.info(session)
    assert len(step_ids) == 2


def test_steps_info(auth):
    """В уроке два шага. И это правильные шаги."""
    session = Session()
    lesson = Lesson(lesson_id=LESSON_ID)
    steps = lesson.steps_info(session)
    assert len(steps) == 2
    for pos, step in enumerate(steps, 1):
        assert step['position'] == pos
        assert step['id'] == STEP_IDS[pos - 1]


def test_step_update(auth):
    lesson_text_steps = generate_lesson_text_steps(2)
    session = Session()

    lesson = Lesson(lesson_id=LESSON_ID)
    max_position = len(lesson_text_steps)
    positions = range(1, max_position + 1)

    for position, step, step_id in zip(positions, lesson_text_steps, STEP_IDS):
        step.update(session=session, lesson_id=LESSON_ID, step_id=step_id, position=position)

    new_lesson_info, new_step_ids = lesson.info(session)
    assert STEP_IDS == new_step_ids
    new_steps_info = lesson.steps_info(session)
    for step_info, step in zip(new_steps_info, lesson_text_steps):
        assert step_info['block']['text'] == f'<p>{step.text}</p>'

def test_step_update_create_delete(auth):
    """Делаем урок на два шага длиннее, добавляем шаги, проверка, удаляем шаги, проверка."""
    lesson = Lesson(lesson_id=LESSON_ID)
    session = Session()
    old_lesson_info, old_step_ids = lesson.info(session)
    old_max_position = len(old_step_ids)
    new_max_position = old_max_position + 2

    lesson_more_text_steps = generate_lesson_text_steps(new_max_position)
    lesson_old_text_steps = lesson_more_text_steps[:-2]

    # добавим два шага
    lesson_more_text_steps[-2].create(session, lesson_id=LESSON_ID, position=old_max_position+1)
    lesson_more_text_steps[-1].create(session, lesson_id=LESSON_ID, position=old_max_position+2)

    # проверим, что шаги добавились
    new_lesson_info, new_step_ids = lesson.info(session)
    assert len(new_step_ids) == new_max_position
    new_steps_info = lesson.steps_info(session)
    for step_info, step in zip(new_steps_info[-2:], lesson_more_text_steps[-2:]):
        assert step_info['block']['text'] == f'<p>{step.text}</p>'

    # убираем два шага
    lesson_more_text_steps[-2].delete(session, step_id=new_step_ids[-2])
    lesson_more_text_steps[-1].delete(session, step_id=new_step_ids[-1])

    # проверяем, что урок возвратился к исходному состоянию
    new_lesson_info, new_step_ids = lesson.info(session)
    assert len(new_step_ids) == len(old_step_ids)
    assert new_step_ids == old_step_ids


def test_lesson_deploy(auth):
    """Делаем урок на два шага длиннее, добавляем шаги, проверка, удаляем шаги, проверка."""
    lesson = Lesson(lesson_id=LESSON_ID)
    session = Session()
    old_lesson_info, old_step_ids = lesson.info(session)
    old_max_position = len(old_step_ids)
    new_max_position = old_max_position + 2

    lesson_more_text_steps = generate_lesson_text_steps(new_max_position)
    lesson_old_text_steps = lesson_more_text_steps[:-2]

    # добавим два шага
    lesson.steps = lesson_more_text_steps
    lesson.deploy(session)

    # проверим, что шаги добавились
    new_lesson_info, new_step_ids = lesson.info(session)
    assert len(new_step_ids) == new_max_position
    new_steps_info = lesson.steps_info(session)
    for step_info, step in zip(new_steps_info, lesson_more_text_steps):
        assert step_info['block']['text'] == f'<p>{step.text}</p>'

    # убираем два шага
    lesson.steps = lesson_old_text_steps
    lesson.deploy(session)

    # проверяем, что урок возвратился к исходному состоянию
    new_lesson_info, new_step_ids = lesson.info(session)
    assert len(new_step_ids) == len(old_step_ids)
    assert new_step_ids == old_step_ids
    new_steps_info = lesson.steps_info(session)
    for step_info, step in zip(new_steps_info, lesson_old_text_steps):
        assert step_info['block']['text'] == f'<p>{step.text}</p>'

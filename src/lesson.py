"""Lesson with several various steps."""
import logging

import pyparsing as pp

from src.logged_requests import LOGGER_NAME, LoggedSession
from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.stepik_api import StepikSession


logger = logging.getLogger(LOGGER_NAME)


class Lesson:
    def __init__(self, position: int | None = None, lesson_id: int = 0):
        self.position = position    # номер шага урока, начиная с 1, None - если все шаги
        self.lesson_id = lesson_id  # id урока
        self.steps: list[Step] = []  # шаги урока
        self.title: str = ''        # заголовок урока (в левом меню)
        # TODO: перенести в конфиги, минимум куда-нибудь в переменную класса или модуля
        self.task_language = 'python3.12'

    #################################################################
    # Stepik API wrappers
    #################################################################
    def info(self, session: StepikSession) -> (dict, list[int]):
        """Информация об уроке в целом"""
        lesson_info = session.fetch_object('lesson', self.lesson_id)
        step_ids = lesson_info['steps']
        return lesson_info, step_ids

    def steps_info(self, session: StepikSession) -> list[dict]:
        """Информация о всех шагах урока."""
        lesson_info, step_ids = self.info(session)
        steps = session.fetch_objects('step-source', step_ids)
        logger.info(steps)
        return steps

    def deploy(self, session: StepikSession):
        """Загружает один или все шаги на Stepik."""

        old_lesson_info, old_step_ids = self.info(session)
        old_length = len(old_step_ids)
        new_length = len(self.steps)
        update_length = min(old_length, new_length)

        logger.info(f'UPDATE from 0 till {update_length} steps {old_step_ids[:update_length]}')
        for i in range(update_length):
            self.steps[i].update(session, lesson_id=self.lesson_id, step_id=old_step_ids[i], position=i+1)

        if update_length < old_length:
            logger.info(f'DELETE from {update_length} till {old_length} steps {old_step_ids[update_length:old_length]}')
            for i in range(update_length, old_length):
                Step.delete(session, step_id=old_step_ids[i])

        if update_length < new_length:
            logger.info(f'CREATE from {update_length} till {new_length} steps')
            for i in range(update_length, new_length):
                self.steps[i].create(session, lesson_id=self.lesson_id, position=i+1)

    def validate_lesson_id(self, lesson_id: int):
        """Проверяем, что новый lesson_id не противоречит предыдущей информации и ID определен"""
        # print(f'{lesson_id=} {self.lesson_id=}')
        # если не даны lesson_id ни в аргументах, ни в файле, ошибка, не знаем куда деплоить
        if not lesson_id and not self.lesson_id:
            parse_error(error_msg='Lesson ID должен быть задан или в файле, или в аргументе --lesson_id ID')

        # оба ID не ноль и разные - пусть авторы разбираются, что куда понаписали
        if lesson_id != self.lesson_id and lesson_id != 0 and self.lesson_id != 0:
            parse_error(error_msg=f'Переопределение lesson ID: в markdown файле равен {self.lesson_id}, в аргументе/toc {lesson_id}')

        self.lesson_id = max(lesson_id, self.lesson_id)

    #################################################################
    # Markdown parsing
    #################################################################
    def parse_markdown(self, text: str) -> (list[Step], int | None):
        """Разбирает текст и возвращает список шагов и словарь с заданными переменными
        {'lesson_id': nnn, 'lang': www} из файла.
        Если указан position, то все остальные шаги в списке None.
        """

        lesson_info = ParseSchema.parse_document(text)
        print(f'{lesson_info=}')
        # res=[{
        #   'title': 'Урок 1',
        #   'variables': {'lesson': '123', 'lang': 'python3.10'}
        #   'steps': [
        #       {'h2': ' Шаг 1', 'text': '\nСодержимое шага один.\n'},
        #       {'h2': ' SKIP Шаг 2 пропускаем', 'text': '\nВторой шаг.\nПишем много чего интересного\n'},
        #       {'h2': ' TEXT Шаг третий', 'text': '\n\nТут много пустых строк.\n\nКоторые нужно тоже обработать.'}
        #   ]
        #   }]
        variables = lesson_info['variables']
        self.title = lesson_info['title']
        if 'lang' in variables:
            self.task_language = variables['lang']
        if 'lesson' in variables:
            self.validate_lesson_id(lesson_id=int(variables['lesson']))
        else:
            self.validate_lesson_id(lesson_id=0)

        self.steps = []
        for entity in lesson_info['steps']:
            ok, step_type, skip, h2 = ParseSchema.parse_step_header(entity['h2'])
            print(f'{ok=}, {step_type=}, {skip=}, {h2=}')
            step = Step.create_by_type(step_type=step_type, header=h2, skip=skip)
            if not skip:
                step.parse(entity['text'])
            self.steps.append(step)

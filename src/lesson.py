"""Lesson with several various steps."""
import logging
import sys

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

    def deploy(self, session: StepikSession, step_position: int = 0):
        """Загружает один или все шаги на Stepik.
        step_position - позиция ОДНОГО шага, который UPDATE (остальные пропускаем):
        * нумерация с 1
        * 0 - все шаги (UPDATE, DELETE, CREATE)
        При попытке CREATE или DELETE одного шага, программа останавливается.
        """

        old_lesson_info, old_step_ids = self.info(session)
        old_length = len(old_step_ids)
        new_length = len(self.steps)
        update_length = min(old_length, new_length)

        print(f"DEPLOY lesson {self.lesson_id}")
        # Проверяем, что деплой одного шага не приходится на удаление или создание шага
        if step_position > new_length:
            print(f'Нельзя удалить один шаг урока {self.lesson_id} на позиции {step_position}. \
            Запустите загрузку всего урока для удаления лишних шагов в конце или удалите лишние шаги вручную.')
            sys.exit(1)
        if step_position > old_length:
            print(f'Нельзя создать один шаг урока {self.lesson_id} на позиции {step_position}. \
            Запустите загрузку всего урока для создания шагов или создайте недостающие шаги вручную.')
            sys.exit(1)

        # если один шаг, то только UPDATE
        if step_position:
            self.steps[step_position-1].update(
                session,
                lesson_id=self.lesson_id,
                step_id=old_step_ids[step_position-1],
                position=step_position)
            # после апдейта конкретного шага больше делать нечего, выходим
            return

        # сюда доходим только если надо деплоить весь урок
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
    def parse_markdown(self, text: str, step_position: int = 0) -> (list[Step], int | None):
        """Разбирает текст и возвращает список шагов и словарь с заданными переменными
        {'lesson_id': nnn, 'lang': www} из файла.
        Если указан step_position, то все остальные шаги в списке не парсятся:
        * 0 - все шаги,
        * от 1 и далее - позиция шага с начала,
        * от -1 и далее - позиция шага с конца
        """

        lesson_info = ParseSchema.parse_document(text)
        # print(f'{lesson_info=}')
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
        step_position = self.make_position_positive(step_position)
        for position, entity in enumerate(lesson_info['steps'], 1):
            ok, step_type, skip, h2 = ParseSchema.parse_step_header(entity['h2'])
            # print(f'{ok=}, {step_type=}, {skip=}, {h2=}')
            step = Step.create_by_type(step_type=step_type, header=h2, skip=skip)

            # парсим только если не SKIP и надо парсить все или нужный номер позиции
            if not skip and (step_position == 0 or position == step_position):
                step.parse(entity['text'])
            self.steps.append(step)

    def make_position_positive(self, step_position: int):
        """Если step_position < 0, то возвращает положительную позицию этого шага (нумеруем с 1)."""
        if step_position >= 0:
            return step_position
        # переводим номер позиции из отрицательной в положительную
        return len(self.steps) + step_position + 1

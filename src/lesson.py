"""Lesson with several various steps."""
import logging

import pyparsing as pp

from src.logged_requests import LOGGER_NAME
from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.stepik_api import Session


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
    def info(self, session: Session) -> (dict, list[int]):
        """Информация об уроке в целом"""
        lesson_info = session.fetch_object('lesson', self.lesson_id)
        step_ids = lesson_info['steps']
        return lesson_info, step_ids

    def steps_info(self, session: Session) -> list[dict]:
        """Информация о всех шагах урока."""
        lesson_info, step_ids = self.info(session)
        steps = session.fetch_objects('step-source', step_ids)
        logger.info(steps)
        return steps

    def deploy(self, session: Session):
        """Загружает один или все шаги на Stepik."""
        old_lesson_info, old_step_ids = self.info(session)
        old_length = len(old_step_ids)
        new_length = len(self.steps)
        update_length = min(old_length, new_length)
        logger.info(f'UPDATE from 0 till {update_length} steps {old_step_ids[:update_length]}')
        for i in range(update_length):
            self.steps[i].update(session, lesson_id=self.lesson_id, step_id=old_step_ids[i], position=i+1)
        logger.info(f'DELETE from {update_length} till {old_length} steps {old_step_ids[update_length:old_length]}')
        for i in range(update_length, old_length):
            Step.delete(session, step_id=old_step_ids[i])
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
    def parse_markdown(self, text: list[str]) -> (list[Step], int | None):
        """Разбирает файл урока с указанным именем и возвращает список шагов и lesson_id урока из файла.
        Если указан position, то все остальные шаги в списке None.
        """
        # skip empty lines
        linenumber = 0
        while text[linenumber] == pp.Empty():
            linenumber += 1
        self.title = ParseSchema.parse_h1(text[linenumber])
        variables, self.steps = self.split_lines_by_h2_and_parse_steps(text[linenumber + 1:])
        # print(variables)
        if 'lang' in variables:
            self.task_language = variables['lang']
        if 'lesson' in variables:
            self.validate_lesson_id(lesson_id=int(variables['lesson']))
        else:
            self.validate_lesson_id(lesson_id=0)

    def split_lines_by_h2_and_parse_steps(self, lines: list[str]) -> (list[Step], dict):
        """Разбивает строки на списки строк по ##, один список - один шаг, разбирает конфиг.
        Возвращает step_list, config
        Структура markdown файла (может быть добавлено в любом месте любое количество пустых строк):
        # Заголовок урока (надо бы его в левом меню писать)
        lesson = 123456    - опционально, lessonID
        lang = python3.12  - опционально, язык задач урока, допускается ANY (без перечисления языка).
        ## TYPE Заголовок шага 1
        содержимое шага
        ## TYPE Заголовок шага 2
        содержимое шага
        Часть TYPE может быть дополнена частью SKIP, что значит, что деплоить этот шаг автоматически запрещено.
        """
        states = (
            'CONFIG',   # заголовок H1 разобран, ждем или строку конфига, или H2
            'BODY'      # читаем тело шага, если натыкаемся на H2 или EOF, заканчиваем предыдущий шаг
        )
        mode = states[0]
        steps = []      # список шагов
        config = {}     # словарь переменных в начале файла
        current_step = None
        step_text = []  # строки текущего шага

        def end_of_step(step: Step, text: list[str], current_position: int):
            """Дошли до конца тела шага, шаг разобрать и добавить в список шагов."""
            if step is None:
                return
            # честно разбираем только те шаги, которые собираемся деплоить
            if self.position is None or self.position == current_position:
                step.parse(text)
            steps.append(step)

        position = 0
        for line_number, line in enumerate(lines, 2):
            # сначала обработаем пустые строки, не двигать, ибо собьется переход с CONFIG на BODY
            if line == pp.Empty():
                if mode == 'BODY':
                    step_text.append(line)
                continue

            # обрабатываем variable=value пока не закончатся (пустые строки обработали выше)
            if mode == 'CONFIG':
                ok, variable, value = ParseSchema.parse_variable_value(line)
                if ok:
                    config[variable] = value
                else:
                    mode = 'BODY'

            # обрабатываем шаги: h2 - новый шаг, добавляем в список уже сделанный шаг
            # иначе добавляем строку в список строк шага
            if mode == 'BODY':
                ok, skip, step_type, header = ParseSchema.parse_step_header(line)
                if ok:
                    end_of_step(current_step, step_text, position)
                    current_step = Step.create_by_type(step_type=step_type, header=header, skip=skip)
                    step_text = []
                    # в конце, потому что мы добавили изначальный current_step=None с position=0
                    position += 1
                else:
                    step_text.append(line)

        # последний шаг, закончен концом файла
        end_of_step(current_step, step_text, position)
        return config, steps

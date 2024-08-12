"""Lesson with several various steps."""

import sys

from src.step import Step


class Lesson:
    def __init__(self, filename: str, position: int | None = None, lesson_id: int = 0):
        self.position = position
        self.steps, self.lesson_id = self.parse(filename, position)
        # если не даны lesson_id ни в аргументах, ни в файле, ошибка, не знаем куда деплоить
        if not lesson_id:
            if not self.lesson_id:
                print('Lesson ID должен быть задан или в файле, или в аргументе --lesson_id ID')
                sys.exit(1)
        else:
            self.lesson_id = lesson_id

    def parse(self, filename: str, position: int | None = None) -> (list[Step], int | None):
        """Разбирает файл урока с указанным именем и возвращает список шагов и lesson_id урока из файла.
        Если указан position, то все остальные шаги в списке None.
        """
        with open(filename, 'r', encoding='utf8') as fin:
            lines = fin.readlines()
        step_parts, config, title = self.split_lines_by_h2(lines)
        # другие степы, кроме position, не парсим, храним None
        steps = [Step.parse(step_lines) if pos+1 == position else None for pos, step_lines in enumerate(step_parts)]

        return position, config.get('lesson', None)

    def deploy(self):
        """Загружает один или все шаги на Stepik."""
        pass

    @staticmethod
    def split_lines_by_h2(self, lines):
        """Разбивает строки на списки строк по ##, один список - один шаг, разбирает конфиг.
        Возвращает step_list, config, h1
        """
        return [], {}, ''

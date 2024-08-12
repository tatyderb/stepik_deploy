"""Lesson with several various steps."""

import sys

class Lesson:
    def __init__(self, filename: str, position: int | None = None, id: int = 0):
        self.position = position
        self.steps, self.id = self.parse(filename, position)
        # если не даны id ни в аргументах, ни в файле, ошибка, не знаем куда деплоить
        if not id:
            if not self.id:
                print('Lesson ID должен быть задан или в файле, или в аргументе --id ID')
                sys.exit(1)
        else:
            self.id = id

    def parse(self, filename: str, position: int | None = None):
        """Разбирает файл урока с указанным именем и возвращает список шагов.
        Если указан position, то все остальные шаги в списке None.
        """
        return [], None

    def deploy(self):
        """Загружает один или все шаги на Stepik."""
        pass

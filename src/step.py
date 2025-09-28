from abc import abstractmethod, ABC
import sys

from src.utils import markdown_to_html
from src.stepik_api import StepikSession


class Step(ABC):
    STEP_TYPES = ['QUIZ', 'CHOICE', 'TEXT', 'STRING', 'NUMBER', 'TASKINLINE']

    def __init__(self, header: str = '', skip: bool = False):
        self.header = header  # текст заголовка шага без ##
        self.skip = skip  # надо ли пропускать шаг при деплое
        self.lines = []  # строки содержимого шага в формате markdown
        self.text = ''  # html текст
        self.config = {}    # словарь опций конфигурации (есть общая часть по всем шагам, есть отдельная по типам шагов)

    def __repr__(self):
        return f'skip={self.skip}\nheader={self.header}\nlines={self.lines}\ntext={self.text}'

    @abstractmethod
    def parse(self, lines: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """to body"""
        pass

    @classmethod
    def create_by_type(cls, step_type: str = 'TEXT', header: str = '', skip: bool = False, step_body: str=''):
        match step_type:
            case 'TEXT':
                return StepText(header=header, skip=skip)
            case 'NUMBER':
                from src.step_number import StepNumber
                return StepNumber(header=header, skip=skip)
            case 'QUIZ':
                from src.step_quiz import StepQuiz
                return StepQuiz(header=header, skip=skip)
            case 'TASKINLINE':
                from src.step_tasklinline import StepTaskinline
                return StepTaskinline(header=header, skip=skip)
            case '_':
                raise NotImplemented(f'Step type {step_type}')

    #################################################################
    # Stepik API wrappers
    #################################################################
    def body(self, lesson_id: int, position: int) -> dict:
        body = self.to_dict()
        body['stepSource']['lesson'] = lesson_id
        body['stepSource']['position'] = position
        return body

    def info(self, session: StepikSession, step_id: int) -> dict:
        """GET step info."""
        step_info = session.fetch_object('step', step_id)
        return step_info

    def update(self, session: StepikSession, lesson_id: int, step_id: int, position: int):
        """Update step."""
        if self.skip:
            print(f'SKIP UPDATE step: {step_id=}, {position=}, {lesson_id=}')
            return
        print(f'UPDATE step: {step_id=}, {position=}, {lesson_id=}')
        body = self.body(lesson_id, position)
        session.update_object('step-sources', step_id, body)

    def create(self, session: StepikSession, lesson_id: int, position: int) -> int:
        """Create step in lesson_id at position (start with 1).
        Return new step ID.
        """
        if self.skip:
            print(f'ERROR: SKIP CREATE step: {position=}, {lesson_id=}')
            print(f'Добавьте вручную шаг любого типа на позицию {position} урока {lesson_id} и запустите загрузку еще раз.')
            sys.exit(1)

        print(f'CREATE step: {position=}, {lesson_id=}')
        body = self.body(lesson_id, position)
        step_id = session.create_object('step-sources', body)
        print(f'NEW {step_id=}')
        return step_id

    @staticmethod
    def delete(session: StepikSession, step_id: int):
        """Update step."""
        print(f'DELETE step: {step_id=}')
        session.delete_object('step-sources', step_id)


class StepText(Step):
    BODY = {
        'stepSource': {
            'block': {
                'name': 'text',                 # тип шага
                'text': 'Hello World!'          #
            },
            'lesson': 0,
            'position': 1
        }
    }

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        markdown_text = '## ' + self.header + '\n' + text
        self.text = markdown_text

    def to_dict(self) -> dict:
        d = self.BODY.copy()
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        return d

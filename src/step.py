from abc import abstractmethod, ABC

from src.utils import markdown_to_html
from src.stepik_api import Session


class Step(ABC):
    STEP_TYPES = ['QUIZ', 'CHOICE', 'TEXT', 'STRING', 'NUMBER', 'TASKINLINE']

    def __init__(self, header: str = '', skip: bool = False):
        self.header = header  # текст заголовка шага без ##
        self.skip = skip  # надо ли пропускать шаг при деплое
        self.lines = []  # строки содержимого шага в формате markdown
        self.text = ''  # html текст

    def __repr__(self):
        return f'skip={self.skip}\nheader={self.header}\nlines={self.lines}\ntext={self.text}'

    @abstractmethod
    def parse(self, lines: list[str]):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """to body"""
        pass

    @classmethod
    def create_by_type(cls, step_type: str = 'TEXT', header: str = '', skip: bool = False):
        match step_type:
            case 'TEXT':
                return StepText(header=header, skip=skip)
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

    def info(self, session: Session, step_id: int) -> dict:
        """GET step info."""
        step_info = session.fetch_object('step', step_id)
        return step_info

    def update(self, session: Session, lesson_id: int, step_id: int, position: int):
        """Update step."""
        print(f'UPDATE step: {step_id=}, {position=}, {lesson_id=}')
        body = self.body(lesson_id, position)
        session.update_object('step-sources', step_id, body)

    def create(self, session: Session, lesson_id: int, position: int) -> int:
        """Create step in lesson_id at position (start with 1).
        Return new step ID.
        """
        print(f'CREATE step: {position=}, {lesson_id=}')
        body = self.body(lesson_id, position)
        step_id = session.create_object('step-sources', body)
        print(f'NEW {step_id=}')
        return step_id

    @staticmethod
    def delete(session: Session, step_id: int):
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

    def parse(self, lines: list[str]):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        self.lines = lines
        markdown_text = '\n'.join(['## ' + self.header] + self.lines)
        self.text = markdown_text
        # self.html = markdown_to_html(markdown_text)

    def to_dict(self) -> dict:
        d = self.BODY.copy()
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        return d

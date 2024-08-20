from abc import abstractmethod, ABC

from src.utils import markdown_to_html


class Step(ABC):
    STEP_TYPES = ['QUIZ', 'CHOICE', 'TEXT', 'STRING', 'NUMBER', 'TASKINLINE']

    def __init__(self, header: str = '', skip: bool = False):
        self.header = header    # текст заголовка шага без ##
        self.skip = skip        # надо ли пропускать шаг при деплое
        self.lines = []         # строки содержимого шага в формате markdown
        self.text = ''          # html текст

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
    def update(self, step_id: int):
        """Update step."""



class StepText(Step):
    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, lines: list[str]):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        self.lines = lines
        markdown_text = '\n'.join(['## ' + self.header] + self.lines)
        self.text = markdown_text
        # self.html = markdown_to_html(markdown_text)

    def to_dict(self) -> dict:
        return {}

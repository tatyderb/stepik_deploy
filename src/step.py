from abc import abstractmethod, ABC


class Step(ABC):
    STEP_TYPES = ['QUIZ', 'CHOICE', 'TEXT', 'STRING', 'NUMBER', 'TASKINLINE']

    def __init__(self, header: str = '', skip: bool = False):
        self.header = header    # текст заголовка шага без ##
        self.skip = skip        # надо ли пропускать шаг при деплое
        self.lines = []         # строки содержимого шага в формате markdown
        self.text = ''          # html текст

    @abstractmethod
    def parse(self, lines: list[str]):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """to body"""
        pass

    @classmethod
    def create(cls, step_type: str = 'TEXT', header: str = '', skip: bool = False):
        match step_type:
            case 'TEXT':
                return StepText(header=header, skip=skip)


class StepText(Step):
    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, lines: list[str]):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        markdown_text = '\n'.join(['## ' + self.header] + self.lines)
        self.text = markdown_text

    def to_dict(self) -> dict:
        return {}

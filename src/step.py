class Step:
    @staticmethod
    def parse(lines: list[str]):
        return StepText(lines)


class StepText(Step):
    def __init__(self, lines: list[str]):
        self.text = ''

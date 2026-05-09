import pytest

from src.step_gennumber import StepGennumber, ParseSchemaStepGennumber


class TestExtractSolveAndMaxError:
    
    @pytest.fixture
    def step(self):
        return StepGennumber()
    
    @pytest.mark.parametrize("answer, expected_solve, expected_max_error", [
        ('\nx+y +- 4\n', 'x+y', 4),
        ('\nx+y +- v\n', 'x+y +- v', 0),
        ('\nx+y +- 1 +- 4\n', 'x+y +- 1', 4),
        ('\nx+y +- 1 +- 4.5\n', 'x+y +- 1', 4.5),
        ('\nx+y\n', 'x+y', 0),

        ('', '', 0),
        ('+-', '+-', 0),
    ])
    def test_extract_solve_and_max_error(self, step, answer, expected_solve, expected_max_error):
        solve, max_error = step._extract_solve_and_max_error(answer)
        assert solve == expected_solve
        assert max_error == expected_max_error
        

text1 = r'''
CONDITION
В саду цветут яблони и груши.
Пчела опылила \x цветочков, а шмель \y.
Сколько цветочков они опылили вместе?

ANSWER 
x+y

VAR
x (1, 20, 1)
y (1, 15, 1)

CONFIG
score: 2
'''
text2 = r'''
CONDITION
В саду цветут яблони и груши.
Пчела облетела яблоню по траектории с радиусом \r м
Какой путь пролетела пчела в сантиметрах?

ANSWER
3.14 * 100 * r +- 1

VAR
r (0.2, 2, 0.1)
'''

def test_parse_step_gennumber():
    res = ParseSchemaStepGennumber.parse_step_gennumber(text1)
    print(f'\nparse_step_gennumber: {res=}')
    expected_dict = {
        'task': 'CONDITION\nВ саду цветут яблони и груши.\nПчела опылила \\x цветочков, а шмель \\y.\nСколько цветочков они опылили вместе?\n', # т.к. разделение условия на части происходит на следующей стадии
        'answer': ' \nx+y\n',
        'ranges': 
        [
            {
                'range': [1, 20, 1],
                'var': 'x'
            },
            {
                'range': [1, 15, 1],
                'var': 'y'
            }
        ],
        'config': {'score': '2'}
    }
    assert res == expected_dict
    res = ParseSchemaStepGennumber.parse_step_gennumber(text2)
    print(f'\nparse_step_gennumber: {res=}')
    expected_dict = {
        'task': 'CONDITION\nВ саду цветут яблони и груши.\nПчела облетела яблоню по траектории с радиусом \\r м\nКакой путь пролетела пчела в сантиметрах?\n',
        'answer': '\n3.14 * 100 * r +- 1\n',
        'ranges': 
        [
            {
                'var': 'r',
                'range': [0.2, 2, 0.1]
            }
        ]
    }
    assert res == expected_dict
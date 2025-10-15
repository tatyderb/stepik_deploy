import inspect
import types

# from test.test_checker import test_encode


def check_asis(reply, clue):
    """Сравнение текста, без пробельных символов в конце текста."""
    return reply.strip() == clue.strip()

def check_int_seq(reply, clue):
    """Сравнение последовательности целых чисел."""
    reply_numbers = list(map(int, reply.split()))
    clue_numbers = list(map(int, clue.split()))

    if len(reply_numbers) != len(clue_numbers):
        return False, f'Output  : {len(reply_numbers)} numbers\nExpected: {len(clue_numbers)} numbers'

    for reply_x, clue_x in zip(reply_numbers, clue_numbers):
        if reply_x != clue_x:
            return False, f'Output  : {reply_x}\nExpected: {clue_x}\n'
    return True

# EPS - additional_parameter для check_float_seq
EPS: float = 0.001
def check_float_seq(reply, clue):
    """Сравнение последовательности нецелых чисел с точностью EPS, по умолчанию 0.001.
    EPS для чекера можно задать в секции CONFIG через additional_params
    additional_params: "EPS=0.01"
    """

    import math

    reply_numbers = list(map(float, reply.split()))
    clue_numbers = list(map(float, clue.split()))

    if len(reply_numbers) != len(clue_numbers):
        return False, f'Output  : {len(reply_numbers)} numbers\nExpected: {len(clue_numbers)} numbers\n'

    for reply_x, clue_x in zip(reply_numbers, clue_numbers):
        if not math.isclose(reply_x, clue_x, abs_tol=EPS):
            return False, f'Output  : {reply_x}\nExpected: {clue_x}\nAccuracy: {EPS}\n'
    return True

def get_checker_function_by_name(name: str) -> types.FunctionType:
    """По названию чекера name возвращает указатель на функцию. С валидацией."""
    available_checkers = {
        'check_asis': check_asis,
        'check_int_seq': check_int_seq,
        'check_float_seq': check_float_seq,
    }
    if name not in available_checkers.keys():
        error_msg = f'Чекер {name} не найден. Доступные чекеры: {available_checkers.keys()}'
        print(error_msg)
        raise ValueError(error_msg)

    return available_checkers[name]

def stepik_genchecksolve(checker_function: types.FunctionType, additional_parameter='') -> str:
    """Степик по умолчанию вставляет это содержимое при создании задачи на программирование,
    добавляя реализацию и вызов функции checker_function_name."""
    source_code = inspect.getsource(checker_function)
    return f"""
{additional_parameter}
{source_code}        
        
# This is a sample Code Challenge
# Learn more: https://stepik.org/lesson/9172
# Ask your questions via help@stepik.org

def generate():
    return []

def check(reply, clue):
    return {checker_function.__name__}(reply, clue)

# def solve(dataset):
#     a, b = dataset.split()
#     return str(int(a) + int(b))        
    """


def custom_genchecksolve(tests: list[list],
                         checker_function: types.FunctionType, additional_parameter='',
                         open_tests: int = -1) -> str:
    """Генерируем тесты сами в generate, добавляя номера тестов.
    Чтобы в check или печатать всю информацию для открытых тестов, или тесты закрытые.
    """

    source_code = inspect.getsource(checker_function)
    encoded_tests = encode_tests(tests, open_tests)
    test_data = '''
Входные данные: 
{test_input}

Ваш ответ:
{reply}

Верный ответ:
{test_output}

'''

    return f"""
{additional_parameter}
{source_code}        

# Learn more: https://stepik.org/lesson/9172
# Ask your questions via help@stepik.org
# Образец кода от Александра Шибаева https://stepik.org/users/387384976/profile

my_tests = {tests}
my_encoded_tests = {encoded_tests}

def generate():
    return [(t[0], ent) for t, ent in zip(my_tests, my_encoded_tests)]

def check(reply, clue):
    # раскодируем закодированные данные теста clue = (input, output, test_number, is_open_test)
    coded_test = clue
    first_line, _, text = coded_test.partition('\\n')
    test_number, _, is_open = first_line.partition(' ')
    test_input, _, test_output = text.partition('----\\n')
    
    res_check = {checker_function.__name__}(reply, test_output)
    # некоторые чекеры возвращают ok/fail + разницу в виде строки
    if isinstance(res_check, bool):
        ok, diff = res_check, ''
    else:
        ok, diff = res_check
        
    if ok:
        return True
    
    # формируем сообщение об ошибке
    if is_open:
        optional = f\"\"\"{test_data}\"\"\"
        if diff:
            optional += 'Разница:\\n\' + diff
    else:
        optional = ""
    return False, optional

# def solve(dataset):
#     a, b = dataset.split()
#     return str(int(a) + int(b))        
    """

def encode_tests(tests: list[list], open_tests: int = -1) -> list[str]:
    """Encode tests = [['input1', 'output1'], ['input2', 'output2']] to list of strings as
1 0
input1
----
output1
    где
    1 - номер теста, начинается с 1
    0 (или 1) - закрытый тест или открытый
    open_tests - количество открытых тестов, -1 - открыты все тесты
    """
    if open_tests == -1:
        open_tests = len(tests)
    return [f'{i+1} {int(i < open_tests)}\n{test[0]}----\n{test[1]}' for i, test in enumerate(tests)]

def decode_tests(coded_tests: list[str]) -> list[tuple[str, str, int, int]]:
    """Разбор закодированных clue из формата
1 0
input1
----
output1
    где
    1 - номер теста, начинается с 1
    0 (или 1) - закрытый тест или открытый
    open_tests - количество открытых тестов, -1 - открыты все тесты
    в формат
    [['input1', 'output1', test_number: int, is_open: int]
    """
    res = []
    for coded_test in coded_tests:
        first_line, _, text = coded_test.partition('\n')
        test_number, _, is_open = first_line.partition(' ')
        test_input, _, test_output = text.partition('----\n')
        res.append((test_input, test_output, int(test_number), int(is_open)))

    return res

import inspect
import types


def check_asis(reply, clue):
    """Сравнение текста, без пробельных символов в конце текста."""
    return reply.strip() == clue.strip()

def check_int_seq(replay, clue):
    """Сравнение последовательности целых чисел."""
    replay_numbers = list(map(int, replay.split()))
    clue_numbers = list(map(int, clue.split()))

    if len(replay_numbers) != len(clue_numbers):
        return False, f'Output: {len(replay_numbers)} numbers\nCorrect output: {len(clue_numbers)} numbers'

    for replay_x, clue_x in zip(replay_numbers, clue_numbers):
        if replay_x != clue_x:
            return False, f'Output: {replay_x}\nCorrect output: {clue_x}\n'
    return True

# EPS - additional_parameter для check_float_seq
EPS: float = 0.001
def check_float_seq(replay, clue):
    """Сравнение последовательности нецелых чисел с точностью EPS"""
    import math

    replay_numbers = list(map(float, replay.split()))
    clue_numbers = list(map(float, clue.split()))

    if len(replay_numbers) != len(clue_numbers):
        return False, f'Output: {len(replay_numbers)} numbers\nCorrect output: {len(clue_numbers)} numbers\n'

    for replay_x, clue_x in zip(replay_numbers, clue_numbers):
        if not math.isclose(replay_x, clue_x, abs_tol=EPS):
            return False, f'Output: {replay_x}\nCorrect output: {clue_x}\nAccuracy: {EPS}\n'
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
    return {checker_function.__name__}(replay, clue)

# def solve(dataset):
#     a, b = dataset.split()
#     return str(int(a) + int(b))        
    """

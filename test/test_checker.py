import pytest

from src.checker import (check_asis, check_int_seq, check_float_seq)
import src.checker as checker


@pytest.mark.parametrize("reply, clue, exp_ok, exp_diff", [
    ('hello', 'hello', True, None),
    ('hello    \t\n', 'hello', True, None),
    ('  hello', 'hello', True, None),
    ('Hello, world!   \t\n', 'Hello, world!', True, None),
    ('Hello, \nworld!\n', 'Hello, world!', False, None),
    ('hello', 'Hello', False, None),
])
def test_checker_asis(reply, clue, exp_ok, exp_diff):
    ok = check_asis(reply, clue)
    # diff не вернули, только сошлось или нет
    # ok, diff = (res, None) if isinstance(res, bool) else *res
    assert ok == exp_ok

@pytest.mark.parametrize("reply, clue, exp_ok, exp_diff", [
    ('12', '12', True, None),
    ('12 34', '12\n34', True, None),
    ('12 34', '12 34 56', False, 'Output  : 2 numbers\nExpected: 3 numbers'),
    ('12 35 56', '12 34 56', False, 'Output  : 35\nExpected: 34\n'),
])
def test_checker_int_seq(reply, clue, exp_ok, exp_diff):
    res = check_int_seq(reply, clue)
    # diff не вернули, только сошлось или нет
    ok, diff = (res, None) if isinstance(res, bool) else res
    assert ok == exp_ok
    assert diff == exp_diff

@pytest.mark.parametrize("reply, clue, eps, exp_ok, exp_diff", [
    ('12', '12', 0, True, None),
    ('12.1 34.01', '12.10001\n34.0100003', 0.0001, True, None),
    ('12 34.0', '12 34.1 56', 0.0001, False, 'Output  : 2 numbers\nExpected: 3 numbers\n'),
    ('12 34.5 56', '12 34.4 56', 0.00001, False, 'Output  : 34.5\nExpected: 34.4\nAccuracy: 1e-05\n'),
    ('12 34.5 56', '12 34.4 56', 0.11, True, None),
])
def test_checker_float_seq(reply, clue, eps, exp_ok, exp_diff):
    checker.EPS = eps
    res = check_float_seq(reply, clue)
    # diff не вернули, только сошлось или нет
    ok, diff = (res, None) if isinstance(res, bool) else res
    assert ok == exp_ok
    assert diff == exp_diff


def test_mode_stepik_genchecksolve():
    """TODO: починить тест, ибо то что напечатанный text внесен в expected_text, но assert не проходит из-за \n"""
    text = checker.stepik_genchecksolve(check_float_seq, 'EPS = 0.02')
    print(text)
    expected_text = '''
EPS = 0.02
def check_float_seq(replay, clue):
    """Сравнение последовательности нецелых чисел с точностью EPS"""
    import math

    replay_numbers = list(map(float, replay.split()))
    clue_numbers = list(map(float, clue.split()))

    if len(replay_numbers) != len(clue_numbers):
        return False, f'Output  : {len(replay_numbers)} numbers\nCorrect Output  : {len(clue_numbers)} numbers\n'

    for replay_x, clue_x in zip(replay_numbers, clue_numbers):
        if not math.isclose(replay_x, clue_x, abs_tol=EPS):
            return False, f'Output  : {replay_x}\nCorrect Output  : {clue_x}\nAccuracy: {EPS}\n'
    return True
        
        
# This is a sample Code Challenge
# Learn more: https://stepik.org/lesson/9172
# Ask your questions via help@stepik.org

def generate():
    return []

def check(reply, clue):
    return check_float_seq(replay, clue)

# def solve(dataset):
#     a, b = dataset.split()
#     return str(int(a) + int(b))        

'''
    # assert expected_text == text

@pytest.mark.parametrize('tests, open_tests, encoded_tests', [
    ([['2 3\n', '5\n'], ['-7 3\n', '-4\n']], -1, ['1 1\n2 3\n----\n5\n', '2 1\n-7 3\n----\n-4\n']),
    ([['2\n3\n', '5\n-1\n'], ['-7\n3\n', '-4\n-10\n']], 1, ['1 1\n2\n3\n----\n5\n-1\n', '2 0\n-7\n3\n----\n-4\n-10\n'])
])
def test_encode(tests, open_tests, encoded_tests):
    encoded_res = checker.encode_tests(tests, open_tests)
    print(encoded_res)
    assert encoded_tests == encoded_res

@pytest.mark.parametrize('tests, encoded_tests', [
    ([('2 3\n', '5\n', 1, 1), ('-7 3\n', '-4\n', 2, 1)], ['1 1\n2 3\n----\n5\n', '2 1\n-7 3\n----\n-4\n']),
    ([('2\n3\n', '5\n-1\n', 1, 1), ('-7\n3\n', '-4\n-10\n', 2, 0)], ['1 1\n2\n3\n----\n5\n-1\n', '2 0\n-7\n3\n----\n-4\n-10\n'])
])
def test_decode(tests, encoded_tests):
    decoded_tests = checker.decode_tests(encoded_tests)
    print(decoded_tests)
    assert tests == decoded_tests




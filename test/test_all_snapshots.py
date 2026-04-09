"""
Сравниваем результаты to_dict() шагов файлов из ../examples
с эталонами из ../src/verification/snapshots
"""

from pathlib import Path

import pytest

from src.lesson import Lesson
from src.verification.snapshops_manager import SnapshotManager, StatusLesson

# base_dir/examples
base_dir = Path(__file__).parent.parent.resolve()
markdown_dir = base_dir / 'examples'
snapshot_dir = base_dir / 'src' / 'verification' / 'snapshots'

@pytest.mark.parametrize('markdown_filename', [
    'step_first.md',
    'step_second.md',
    'step1_markdown.md',
    'step2_match.md',
    'step2_quiz.md',
    'step2_sort.md',
    'step2_table.md',
    'step3_space.md',
    'step3_number.md',
    'step3_string.md',
    'step3_essay.md',
    'step4_taskinline.md',
])
def test_compare_with_snapshot(markdown_filename):
    manager = SnapshotManager()
    assert StatusLesson.PASSED == manager.check_lesson(markdown_dir / markdown_filename)

@pytest.mark.step_begin("---1234")
@pytest.mark.parametrize('markdown_filename', [
    'step_first.md',
    'step_second.md',
    # 'step1_markdown.md',
    # 'step2_match.md',
    # 'step2_quiz.md',
    # 'step2_sort.md',
    # 'step2_table.md',
    # 'step3_essay.md',
    # 'step3_number.md',
    # 'step3_string.md',
    # 'step4_taskinline.md',
])
def test_compare_dumps_with_snapshot(markdown_filename):
    manager = SnapshotManager()
    assert StatusLesson.PASSED == manager.check_lesson_dump(markdown_dir / markdown_filename)




"""
Тесты для проверки цикла markdown -> Stepik -> markdown с использованием снапшотов.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest

from src.verification.dump_manager import verify_dump
from src.verification.snapshops_manager import Verbose

base_dir = Path(__file__).parent.parent.resolve()
markdown_dir = base_dir / "examples"


@pytest.mark.parametrize(
    "markdown_filename",
    [
        "step_first.md",
        "step_second.md",
        #"step1_markdown.md",
        #"step2_quiz.md",
        #"step2_sort.md",
        #"step2_table.md",
        #"step3_essay.md",
        #"step3_number.md",
        #"step3_string.md",
        #"step4_taskinline.md",
    ],
)
def test_dump_verification(markdown_filename):
    """
    Тест проверяет, что урок, скачанный после загрузки, идентичен исходному.
    """
    md_path = markdown_dir / markdown_filename
    result = verify_dump(str(md_path), verbose=Verbose.ERROR)
    assert result is True, f"Тест не пройден для {markdown_filename}"


if __name__ == "__main__":
    print("Запуск тестов...")
    pytest.main([__file__, "-v"])

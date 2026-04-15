"""
Utils for markdown -> html conversion.
"""
import difflib
from datetime import datetime
from pathlib import Path

import markdown  # https://python-markdown.github.io

# максимальная печатаемая длина строки
DEFAULT_MAX_LEN = 80

def markdown_to_html(text_md):
    if not isinstance(text_md, str):               # list of strings
        text_md = '\n'.join(text_md)
    return markdown.markdown(
        text_md,
        extensions=['extra'],
        # extensions=['extra', 'nl2br'],
    #    output_format="html5"
    )

def generate_timestring(date_template: str = "%m%d_%H%M%S"):
    """ Время в формате md_HMS """
    return datetime.now().strftime(date_template)

def truncate(line: str, max_len: int = DEFAULT_MAX_LEN, ignore: bool = False) -> str:
    """Строка не более max_len символов, в конце добавляем ..."""
    if ignore or len(line) <= max_len:
        return line

    return line[:max_len-3] + "..."

def context_diff_files(file1: str | Path, file2: str | Path, context_line_number: int =3) -> str:
    """Вывод различий с n строками контекста"""
    with open(file1, 'r', encoding='utf-8') as f1, \
            open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    diff = difflib.context_diff(lines1, lines2,
                                fromfile=str(file1),
                                tofile=str(file2),
                                n=context_line_number)

    # for s in diff:
    #     print(s, end='')
    return ''.join(diff)


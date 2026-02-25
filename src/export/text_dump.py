import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import read_or_create_auth_data
from src.stepik_api import StepikSession
from src.logged_requests import setup_logger
from html_to_markdown import convert_to_markdown


def fix_latex(text):
    """Исправляет экранированные LaTeX формулы"""
    text = text.replace(r'\(', '$').replace(r'\)', '$')
    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
    text = re.sub(r'\\([=+\-*])', r'\1', text)
    text = text.replace(r'\$', '$')
    return text


def adjust_header_levels(markdown_text, base_level=2):
    """
    Понижает уровни всех заголовков в markdown тексте.
    
    Аргументы:
        markdown_text: текст в формате markdown
        base_level: базовый уровень для заголовков (по умолчанию 2 для ##)
    
    Возвращает:
        текст с пониженными уровнями заголовков
    """
    lines = markdown_text.split('\n')
    result_lines = []
    
    atx_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    
    for line in lines:
        atx_match = atx_pattern.match(line)
        if atx_match:
            hashes = atx_match.group(1)
            title = atx_match.group(2)
            current_level = len(hashes)
            new_level = min(current_level + base_level - 1, 6)
            result_lines.append('#' * new_level + ' ' + title)
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)


def dump_lesson(lesson_id, filename=None):
    
    setup_logger()
    read_or_create_auth_data()
    session = StepikSession()
    
    lesson = session.fetch_object('lesson', lesson_id)
    lesson_title = lesson.get('title', 'Без названия')
    step_ids = lesson.get('steps', [])
    
    if not step_ids:
        return
    
    all_markdown = []
    all_markdown.append(f"# {lesson_title}")
    all_markdown.append("")
    all_markdown.append(f"lesson: {lesson_id}")
    all_markdown.append("")
    
    for i, step_id in enumerate(step_ids, 1):
        try:
            step = session.fetch_object('step-source', step_id)
            block = step.get('block', {})
            html = block.get('text', '')
            
            title_match = re.search(r'<h([1-6])[^>]*>(.*?)</h\1>', html, re.IGNORECASE)
            
            if title_match:
                step_title = title_match.group(2).strip()
                html = html[:title_match.start()] + html[title_match.end():]
            else:
                step_title = f"Шаг {i}"

            text = convert_to_markdown(html, heading_style='atx')
            text = fix_latex(text)

            if text.strip():
                text = adjust_header_levels(text, base_level=3)

            all_markdown.append(f"## {step_title}")
            all_markdown.append(text.strip())
            
        except Exception as e:
            print(f"Ошибка шага {step_id}: {e}")
            pass
    
    if not filename:
        filename = f"lesson_{lesson_id}_dump.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_markdown))
    
    print(f"Дамп сохранен в {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python text_dump.py LESSON_ID [filename]")
        sys.exit(1)
    
    lesson_id = int(sys.argv[1])
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    dump_lesson(lesson_id, filename)
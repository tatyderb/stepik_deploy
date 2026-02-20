import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import read_or_create_auth_data
from src.stepik_api import StepikSession
from src.logged_requests import setup_logger
from html_to_markdown import convert_to_markdown


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
            
            
            title_match = re.search(r'<h2>(.*?)</h2>', html)
            step_title = title_match.group(1) if title_match else f"Шаг {i}"
            
            if title_match:
                html = html[:title_match.start()] + html[title_match.end():]

            text = convert_to_markdown(html, heading_style='atx')

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
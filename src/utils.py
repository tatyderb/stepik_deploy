"""
Utils for markdown -> html conversion.
"""
from datetime import datetime
import markdown  # https://python-markdown.github.io

# максимальная печатаемая длина строки
DEFAULT_MAX_LEN = 80

def markdown_to_html(text_md):
    if not isinstance(text_md, str):               # list of strings
        text_md = '\n'.join(text_md)
    return markdown.markdown(
        text_md,
        extensions=['extra', 'nl2br'],
    #    output_format="html5"
    )

def generate_timestring(date_template: str = "%m%d_%H%M%S"):
    """ Время в формате md_HMS """
    return datetime.now().strftime(date_template)

def truncate(line: str, max_len: int = DEFAULT_MAX_LEN) -> str:
    """Строка не более max_len символов, в конце добавляем ..."""
    if len(line) <= max_len:
        return line

    return line[:max_len-3] + "..."

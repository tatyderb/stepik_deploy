"""
Utils for markdown -> html conversion.
"""
from datetime import datetime
import markdown  # https://python-markdown.github.io


def markdown_to_html(text_md):
    if not isinstance(text_md, str):               # list of strings
        text_md = '\n'.join(text_md)
    return markdown.markdown(
        text_md,
        extensions=['extra'],
    #    output_format="html5"
    )

def current_md_hm(date_template: str = "%m%d_%H%M%S"):
    """ Время в формате md_HMS """
    return datetime.now().strftime(date_template)

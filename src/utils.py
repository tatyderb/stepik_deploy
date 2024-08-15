"""
Utils for markdown -> html conversion.
"""

import markdown  # https://python-markdown.github.io


def markdown_to_html(text_md):
    if not isinstance(text_md, str):               # list of strings
        text_md = '\n'.join(text_md)
    return markdown.markdown(
        text_md,
        extensions=['extra'],
    #    output_format="html5"
    )

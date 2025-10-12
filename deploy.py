import click

from src import logged_requests
from src.auth import read_or_create_auth_data
from src.lesson import Lesson
from src.logged_requests import LoggedSession
from src.stepik_api import StepikSession
from src.toc import get_file_from_toc


def get_lesson_file(filename, toc, step): 
    """По разобранным аргументам возвращает имя файла и позицию в уроке (порядковый номер шага).
    Варианты
    deploy.py lesson.md --step 4    # шаг 4 урока
    deploy.py lesson.md             # весь урок
    deploy.py toc.yaml --toc 3.8.12 # шаг 12 урока в разделе 3.8
    deploy.py toc.yaml --toc 3.8    # весь урок в разделе 3.8
    """

    if toc:
        lesson_file, position = get_file_from_toc(toc_file=filename, toc_position=toc)
    else:
        lesson_file = filename
        position = step
    return lesson_file, position


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('filename', type=click.Path(exists=True))
#  Справки на английском (исходные)
@click.option('-s', '--step', type=int, default=0, metavar='STEP',
              help='Update only the step N, start N from 1, numbers <0 as step number are allowed too')
@click.option('-t', '--toc', type=str, default='', metavar='TOC',
              help='Module.lesson[.step] format, e.g 3.8 for whole lesson, or 3.8.2 for step only')
@click.option('--id', 'lesson_id', type=int, default=0, metavar='ID', help='Lesson ID, with markdown file only')
@click.option('-g', '--gift', is_flag=True, default=False, help='Lesson file in GIFT format')
@click.option('--toc-update', is_flag=True, default=False,
              help='Update TOC part in yaml config up to first error.')
# # двуязычные справки
# @click.option('-s', '--step', type=int, default=0, metavar='STEP',
#               help='Update only specific step / Обновить только конкретный шаг\n'
#                    'Start from 1, negative numbers supported / Нумерация с 1, поддерживаются отрицательные номера')
# @click.option('-t', '--toc', type=str, default='', metavar='TOC',
#               help='Position in module.lesson[.step] format / Позиция в формате модуль.урок[.шаг]\n'
#                    'Examples / Примеры: 3.8 (whole lesson / весь урок), 3.8.2 (single step / один шаг)')
# @click.option('--id', 'lesson_id', type=int, default=0, metavar='ID', 
#               help='Lesson ID (for markdown files only) / ID урока (только для markdown файлов)')
# @click.option('-g', '--gift', is_flag=True, default=False, 
#               help='Lesson file in GIFT format / Файл урока в формате GIFT')
# @click.option('--toc-update', is_flag=True, default=False,
#               help='Update TOC in yaml config up to first error / '
#                    'Обновить TOC в yaml конфиге до первой ошибки')
def main(filename, step, toc, lesson_id, gift, toc_update):
    """Deploy markdown or GIFT file into site and other Stepik tools."""

    if step != 0 and toc:
        raise click.UsageError("Options --step and --toc are mutually exclusive")
    
    logged_requests.setup_logger()
    read_or_create_auth_data()

    print(f'Args: filename={filename}, step={step}, toc={toc}, lesson_id={lesson_id}, gift={gift}, toc_update={toc_update}')

    if toc_update:
        print('TOC update not implemented yet!')
        return
    
    lesson_file, position = get_lesson_file(filename, toc, step)
    lesson = Lesson(position=position, lesson_id=lesson_id)
    if gift:
        raise NotImplemented
    else:
        # lesson in markdown format
        with open(lesson_file, 'r', encoding='utf8') as fin:
            text = fin.read()
            lesson.parse_markdown(text, step_position=step)

    session = StepikSession()
    lesson.deploy(session, step_position=step)


if __name__ == '__main__':
    main()

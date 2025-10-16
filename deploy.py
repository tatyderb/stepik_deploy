import click

from src import logged_requests
from src.auth import read_or_create_auth_data
from src.lesson import Lesson
from src.logged_requests import LoggedSession
from src.stepik_api import StepikSession
from src.toc import get_file_from_toc


def get_lesson_file(filename, step, toc: str = ''):
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
HELP_EPILOG = '''\b
Примеры:
  python deploy.py lesson.md                Загрузить весь урок, лежащий в step3_number.md.
  python deploy.py -s 1 lesson.md           Загрузить только первый шаг из этого урока.
  python deploy.py -s -1 lesson.md          Загрузить только последний шаг из этого урока.

\b
Об ошибках сообщайте по адресу: <https://github.com/tatyderb/stepik_deploy/issues>
Репозиторий проекта: <https://github.com/tatyderb/stepik_deploy>
Онлайн курс, демонстрирующий работу с этой утилитой: <https://stepik.org/course/253149>
'''

@click.command(context_settings=CONTEXT_SETTINGS, epilog=HELP_EPILOG)
@click.argument('filename', type=click.Path(exists=True))
@click.help_option('-h', '--help', help='показать эту справку и выйти')
@click.option('-s', '--step', type=int, default=0, metavar='STEP',
              help='обновить только конкретный шаг,\n'
                   'нумерация с 1, поддерживаются отрицательные номера (тогда нумерация с последнего шага)')
# @click.option('-t', '--toc', type=str, default='', metavar='TOC',
#               help='Пока не реализовано! Обновить урок по его TOC, формат module.lesson[.step],\n'
#                    'примеры: 3.8 (весь урок), 3.8.2 (один шаг)')
# @click.option('--id', 'lesson_id', type=int, default=0, metavar='ID',
#               help='Пока не реализовано! ID урока (только для markdown файлов)')
# @click.option('-g', '--gift', is_flag=True, default=False,
#               help='Пока не реализовано! файл урока в формате GIFT')
# @click.option('--toc-update', is_flag=True, default=False,
#               help='Пока не реализовано! обновить TOC в yaml конфиге до первой ошибки')
# def main(filename, step, toc, lesson_id, gift, toc_update):
def main(filename, step):
    """Загрузка markdown или GIFT файла на сайт Stepik (или другие инструменты для работы со Stepik)."""

    # if step != 0 and toc:
    #     raise click.UsageError("Опции --step и --toc взаимоисключающие")
    
    logged_requests.setup_logger()
    read_or_create_auth_data()

    print(f'Args: filename={filename}, step={step}')

    lesson_file, position = get_lesson_file(filename, step)
    lesson = Lesson(position=position)

    # lesson in markdown format
    with open(lesson_file, 'r', encoding='utf8') as fin:
        text = fin.read()
        lesson.parse_markdown(text, step_position=step)

    session = StepikSession()
    lesson.deploy(session, step_position=step)


if __name__ == '__main__':
    main()

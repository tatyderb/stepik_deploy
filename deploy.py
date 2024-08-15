import argparse

from src.auth import read_or_create_auth_data
from src.lesson import Lesson
from src.toc import get_file_from_toc


def get_lesson_file(args):
    """По разобранным аргументам возвращает имя файла и позицию в уроке (порядковый номер шага).
    Варианты
    deploy.py lesson.md --step 4    # шаг 4 урока
    deploy.py lesson.md             # весь урок
    deploy.py toc.yaml --toc 3.8.12 # шаг 12 урока в разделе 3.8
    deploy.py toc.yaml --toc 3.8    # весь урок в разделе 3.8
    """

    if args.toc:
        lesson_file, position = get_file_from_toc(toc_file=args.filename, toc_position=args.toc)
    else:
        lesson_file = args.filename
        position = args.step
    return lesson_file, position


def parse_args():
    """Разбираем аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description='Deploy markdown or GIFT file into site and other Stepik tools.')
    parser.add_argument('filename', metavar='FILE', type=str, help='input file (markdown, gift or yaml)')
    # или step, или toc, подумать, что можно оставить один и разбирать в нем {'module': , 'lesson':, 'step':}
    command_group = parser.add_mutually_exclusive_group()
    command_group.add_argument('-s', '--step', type=int, default=None,
                               help='update only the step N, start N from 1, numbers <0 as step number are allowed too')
    command_group.add_argument('-t', '--toc', type=str, default='',
                               help='module.lesson[.step] format, e.g 3.8 for whole lesson, or 3.8.2 for step only')

    parser.add_argument('--id', type=int, default=0, help='lesson ID, with markdown file only')
    parser.add_argument('-g', '--gift', action='store_true', default=False, help='lesson file in GIFT format')
    parser.add_argument('--toc_update', action='store_true', default=False,
                        help='update TOC part in yaml config up to first error.')

    args = parser.parse_args()
    return args


def main():
    read_or_create_auth_data()
    args = parse_args()
    print('Args=', args)
    if args.toc_update:
        print('TOC update not implemented yet!')
        return
    lesson_file, position = get_lesson_file(args)
    lesson = Lesson(position=position, lesson_id=args.id)
    if args.gift:
        raise NotImplemented
    else:
        # lesson in markdown format
        with open(lesson_file, 'r', encoding='utf8') as fin:
            lines = fin.readlines()
            lesson.parse_markdown(lines)
    lesson.deploy()


if __name__ == '__main__':
    main()

import argparse
import sys

from src.auth import read_or_create_auth_data


def parse_args(argv):
    """Разбираем аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description='Deploy markdown or GIFT file into site and other Stepik tools.')
    parser.add_argument('filename', metavar='FILE', type=str, help='input file (markdown, gift or yaml)')
    parser.add_argument('-s', '--step', type=int,
                        help='update only the step N, start N from 1, negative numbers as step number are allowed too')
    parser.add_argument('--id', type=int, default=0, help='lesson ID')
    parser.add_argument('--gift', action='store_true', help='lesson file in GIFT format')
    parser.add_argument('--toc', type=str,
                        help='module.lesson[.step] format, e.g 3.8 for whole lesson, or 3.8.2 for step only')
    parser.add_argument('--toc-update', action='store_true', help='update TOC part in yaml config up to first error.')

    args = parser.parse_args()
    return args


def main():
    read_or_create_auth_data()
    args = parse_args(sys.argv)
    print(args)


if __name__ == '__main__':
    main()

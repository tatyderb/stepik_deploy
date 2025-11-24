import json
import sys
from enum import StrEnum, IntEnum, auto
from pathlib import Path
from typing import Any
import click

from src.lesson import Lesson
from src.step import Step
from src.utils import truncate

DEFAULT_MAX_LEN = 100
SNAPSHOTS_DIR = "snapshots"
SNAPSHOT_EXTENSION = ".json"
MAX_TEXT_LINES_PREVIEW = 3
SNAPSHOT_ACTION = "Используйте опцию -u для создания снапшота"

class CompareError(Exception):
    pass

# Статусы
class StatusLesson(StrEnum):
    PASSED = "✅ "
    FAILED = "❌ "

class StatusStep(StrEnum):
    PASSED = "✅ "
    FAILED = "❌ "
    SKIP = "➖ "
    # REMOVE = SKIP


class Status(StrEnum):
    UNEXPECTED_SKIP = "skip только в снапшоте"
    PASSED = "passed"
    FAILED = "failed"
    # EXTRA_IN_SNAPSHOT = "extra_in_snapshot"
    # NEW_IN_CURRENT = "new_in_current"
    # SKIPPED_IN_CURRENT = "skipped_in_current"
    SKIP = "skip"
    OUT_OF_RANGE = "разное количество шагов в markdown и снапшоте."
    IN_PROGRESS = "in_progress"  # не должен выходить результат наружу из SnapshotManager с этим статусом

class Verbose(IntEnum):
    ERROR = auto()          # только сообщения об ошибках (в норме ничего)
    SUMMARY = auto()        # только информация pass/fail об уроке
    LESSON = auto()         # урок - количество шагов, из них .. pass, .. fail, .. skip.
    STEP = auto()           # по каждому шагу - pass, fail, skip, расхождение количества шагов, неожиданный skip
    DEBUG = auto()          # разница в полях dict шагов

class SnapshotManager:
    LINE_LESSON_SEPARATOR = "=" * 40
    LINE_STEP_SEPARATOR = "-" * 40
    LINE_DEBUG_SEPARATOR = "." * 40

    def __init__(self, verbose: Verbose = Verbose.ERROR):
        self.snapshots_dir = Path(__file__).parent / SNAPSHOTS_DIR
        self.snapshots_dir.mkdir(exist_ok=True)
        self.__verbose: Verbose = verbose    # нужна ли подробная трассировка сравнения

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, value: Verbose | str | int):
        """Чтобы следить кто и где меняет уровень логирования."""
        if isinstance(value, Verbose):
            self.__verbose = value
        elif isinstance(value, str):
            for level in Verbose:
                if value.upper() == level.name.upper():
                    self.__verbose = level
        elif isinstance(value, int):
            self.__verbose = Verbose(value)

    def trace(self, verbose_level: Verbose = Verbose.DEBUG, msg: str = "", *args, **kwargs):
        """Печатаем, только если verbose_level передан меньше или равен установленному."""
        if verbose_level <= self.verbose:
            print(msg, *args, **kwargs)

    def get_snapshot_path(self, md_filename: str) -> Path:
        """Получает путь к файлу снапшота на основе MD файла"""
        md_path = Path(md_filename)
        snapshot_name = md_path.stem + SNAPSHOT_EXTENSION
        return self.snapshots_dir / snapshot_name

    def create_snapshot(self, md_filename: str) -> str:
        """Создает/обновляет снапшот урока"""

        lesson = Lesson()

        with open(md_filename, 'r', encoding='utf-8') as f:
            lesson.parse_markdown(f.read())

        snapshot_data = {
            "metadata": {
                "source_md": md_filename,
                "total_steps": len(lesson.steps),
                "lesson_id": lesson.lesson_id,
                "title": lesson.title
            },
            "steps": []
        }

        for i, step in enumerate(lesson.steps):
            step_data = "" if step.skip else step.to_dict()

            snapshot_step = {
                "position": i + 1,
                "type": step.__class__.__name__,
                "header": step.header.strip(),
                "skip": step.skip,
                "data": step_data
            }
            snapshot_data["steps"].append(snapshot_step)

        snapshot_path = self.get_snapshot_path(md_filename)
        with open(snapshot_path, 'w', encoding='utf-8') as fout:
            json.dump(snapshot_data, fout, indent=2, ensure_ascii=False)

        return f"Снапшот создан: {snapshot_path}"

    def load_snapshot(self, md_filename: str) -> dict[str, Any]:
        """Загружает снапшот из файла"""
        snapshot_path = None
        try:
            snapshot_path = self.get_snapshot_path(md_filename)
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except OSError as e:
            raise CompareError(f"Ошибка доступа к файлу {snapshot_path}: {e}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise CompareError(f"Ошибка загрузки снапшота {snapshot_path}: {e}")

    def check_lesson(self, markdown_filename: str | Path, step_position: int = 0):
        """Проверяет урок из файла markdown_filename, сравнивая его с существующим снапшотом.
        Если задан step_position, то сравнивается только указанный шаг (нумерация с 1, может быть отрицательным).
        """

        # Читаем снапшот из файла
        try:
            lesson = Lesson()
            with open(markdown_filename, 'r', encoding='utf-8') as f:
                lesson.parse_markdown(f.read(), step_position=step_position)

            snapshot = self.load_snapshot(markdown_filename)
        except CompareError as e:
            self.trace(Verbose.ERROR, str(e))
            return {
                "status": Status.FAILED,
                "message": str(e),
                "action": SNAPSHOT_ACTION
            }

        markdown_steps = lesson.steps
        markdown_length = len(markdown_steps)
        snapshot_steps = snapshot["steps"]
        snapshot_length = len(snapshot_steps)
        step_position = lesson.make_position_positive(step_position=step_position)

        self.trace(Verbose.LESSON,
                   self.LINE_LESSON_SEPARATOR + '\n',
                   f"Урок {markdown_filename}\n",
                    f"\t{snapshot_length} шагов - снапшот файл\n",
                    f"\t{markdown_length} шагов - markdown файл\n"
                   )

        step_results = []

        for position in range(1, 1 + max(markdown_length, snapshot_length)):
            # нужно разобрать только одну позицию, тогда остальные пропускаем

            if step_position and position != step_position:
                msg = f"\t{StatusStep.SKIP} шаг {position}: пропускаем."
                self.trace(Verbose.STEP, msg)
                step_results.append({
                    "status": Status.SKIP,
                    "message": msg
                })
                # на всякий случай, если кто-то нарушит цепочку if..elif..else
                continue

            # в markdown шага нет, ошибка
            elif position > markdown_length:
                msg = f"\t{StatusStep.FAILED} Шаг {position} не существует. Всего шагов: {markdown_length}"
                self.trace(Verbose.STEP, msg)
                step_results.append({
                    "status": Status.OUT_OF_RANGE,
                    "message": msg
                })

            # в снапшоте шага нет, ошибка
            elif position > snapshot_length:
                msg = f"\t{StatusStep.FAILED} Шаг снапшота {position} не существует. Всего шагов: {snapshot_length}"
                self.trace(Verbose.STEP, msg)
                step_results.append({
                    "status": Status.OUT_OF_RANGE,
                    "message": msg
                })

            # пропускаем шаг в markdown (полезно, если он временно не работает и мы пометили его SKIP)
            elif markdown_steps[position - 1].skip:
                msg = f"\t{StatusStep.SKIP} шаг {position}: SKIP - пропускаем"
                self.trace(Verbose.STEP, msg)
                step_results.append({
                    "status": Status.SKIP,
                    "message": msg
                })

            # если шаг пропущен в снапшоте, но есть в markdown - ошибка
            # местами elif с предыдущим не менять!!!
            elif snapshot_steps[position - 1]['skip']:
                msg = f"\t{StatusStep.FAILED} Шаг {position} пропущен в снапшоте, но активен в текущем уроке"
                self.trace(Verbose.STEP, msg)
                step_results.append({
                    "status": Status.UNEXPECTED_SKIP,
                    "message": msg
                })

            # сравниваем содержимое шага в markdown и снапшоте
            else:
                # печать трассировки внутри compare_step
                result = self.compare_step(
                    position,
                    markdown_step=markdown_steps[position - 1],
                    snapshot_step=snapshot_steps[position - 1]
                )
                step_results.append(result)

        # по статусам сравнения шагов вычисляем статус сравнения урока
        result = self.total_results(step_results)
        result['filename'] = str(markdown_filename)
        self.print_lesson_summary(result)
        return result

    def compare_step(self, position: int, markdown_step: Step, snapshot_step: dict) -> dict:
        """Сравнивает содержимое markdown_step.to_dict() и snapshot_step.
        Тип шага, заголовок, содержимое.
        Возвращает {
                "header": snapshot_step["header"],
                "type": snapshot_step["type"],
                "status": Status.FAILED | Status.PASS,
                "message": "Обнаружены различия",
                "differences": differences
            }
        """
        # не совпадает тип шага
        snapshot_step_type = snapshot_step["type"]
        markdown_step_type = markdown_step.__class__.__name__
        if snapshot_step_type != markdown_step_type:
            msg = f"\t{StatusStep.FAILED} Шаг {position}: изменился тип шага {snapshot_step_type} → {markdown_step_type}"
            self.trace(Verbose.STEP, msg)
            return {
                "position": position,
                "header": snapshot_step["header"],
                "status": Status.FAILED,
                "message": msg
            }

        # не совпадает заголовок шага
        snapshot_step_header = snapshot_step["header"]
        markdown_step_header = markdown_step.header.strip()
        if snapshot_step_header != markdown_step_header:
            msg = f"\t{StatusStep.FAILED} Шаг {position}: изменился заголовок шага {snapshot_step_header} → {markdown_step_header}"
            self.trace(Verbose.STEP, msg)
            return {
                "position": position,
                "header": f"{snapshot_step_header} → {markdown_step_header}",
                "status": Status.FAILED,
                "message": msg
            }

        # сравниваем данные
        snapshot_data = snapshot_step["data"]
        markdown_data = markdown_step.to_dict()

        # трассировка внутри сравнения
        if self.compare_dict_as_json(snapshot_data, markdown_data):
            msg = f"\t{StatusStep.PASSED} Шаг {position}: ok"
            self.trace(Verbose.STEP, msg)
            return {
                "position": position,
                "header": snapshot_step["header"],
                "type": snapshot_step["type"],
                "status": Status.PASSED,
                "message": "Шаг соответствует снапшоту"
            }

        msg = f"\t{StatusStep.FAILED} Шаг {position}: обнаружены различия"
        self.trace(Verbose.STEP, msg)
        return {
            "position": position,
            "header": snapshot_step["header"],
            "type": snapshot_step["type"],
            "status": Status.FAILED,
            "message": msg,
        }


    def compare_dict_as_json(self, markdown_dict: dict, snapshot_dict: dict) -> bool:
        """Сравниваем словари рекурсивно до первой разницы или до конца, если разницы нет.
        Возвращает True, если словари одинаковые."""

        # отступ при печати трассировки
        indent = '\t\t'

        md_json = json.dumps(markdown_dict, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
        sn_json = json.dumps(snapshot_dict, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
        for md_line, sn_line in zip(md_json, sn_json):
            if md_line == sn_line:
                self.trace(Verbose.DEBUG, truncate(indent + md_line))
            else:
                self.trace(Verbose.DEBUG, truncate(indent + '+ ' + md_line))
                self.trace(Verbose.DEBUG, truncate(indent + '- ' + sn_line))
                return False

        return True

    def total_results(self, step_results: list[dict]) -> dict:
        """По статусам сравнения шагов вычисляем статус сравнения урока.
        Возвращаем статус сравнения урока вместе со статусами шагов."""
        totals = {
            "status": Status.IN_PROGRESS,
            "steps_verified": 0,
            "steps_passed": 0,
            "steps_failed": 0,
            "steps_skipped": 0,
            "step_results": step_results
        }
        for step in step_results:
            totals['steps_verified'] += 1
            match step['status']:
                case Status.PASSED:
                    totals['steps_passed'] += 1
                case Status.SKIP:
                    totals['steps_skipped'] += 1
                case Status.FAILED:
                    totals['steps_failed'] += 1
                case '_':
                    raise ValueError(f'Unknown step status {step['status']}')

        totals['status'] = StatusLesson.FAILED if totals['steps_failed'] > 0 else StatusLesson.PASSED

        return totals

    def print_lesson_summary(self, result):
        """Трассировка итогов сравнения всех шагов урока."""

        self.trace(Verbose.SUMMARY,
                   self.LINE_STEP_SEPARATOR,
                   f"{result['status']}  Урок: {result['filename']}",
                    f"\tПроверено шагов: {result['steps_verified']}",
                    f"\tPASS: {result['steps_passed']}",
                    f"\tFAIL: {result['steps_failed']}",
                    f"\tSKIP: {result['steps_skipped']}",
                   sep='\n',
                   end='\n'
                )

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

verbose_help = '''\b
Выберите уровень детализации печати:
error - только сообщения об ошибках;
summary - по шагам количество: всего, pass, fail;
lesson - статус по каждому шагу урока;
step - разница в шагах;
debug - подробная разница содержимого шага, до первого различия.
'''

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('filename', type=click.Path(exists=True), required=True)
@click.option('-s', '--step', type=int, default=0, metavar='STEP',
              help='Сверить только конкретный шаг '
              '(нумерация с 1, отрицательные - с конца)')
@click.option('-u', '--update', is_flag=True, help='Обновить/создать снапшот')
@click.option('--verbose',
              type=click.Choice(list(Verbose.__members__), case_sensitive=False),
              default='summary',
              help=verbose_help
)
@click.help_option('-h', '--help', help='Показать эту справку и выйти')
def main(filename: str, step: int, update: bool, verbose: str):
    """Менеджер снапшотов для верификации уроков Stepik"""

    manager = SnapshotManager()
    manager.verbose = verbose

    try:
        if update:
            # Создаем/обновляем снапшот
            result = manager.create_snapshot(filename)
            click.echo(result)

        else:
            manager.check_lesson(markdown_filename=filename, step_position=step)

    except Exception as e:
        click.echo(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

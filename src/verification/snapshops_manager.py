"""
Проверка deploy: конвертация из markdown в body POST запросов для каждого шага.
* Исходный файл в формате markdown в директории examples, например markdown_file=examples/step_first.md
* Ему соответствует образец (snapshot) src/verification/step_first.json, свой формат json
* Читается markdown файл и разбирается на шаги
* Для каждого шага сравнивается Step.to_dict и snapshot['steps'][i]['data']

Подготовка образов (snapshot) - один раз создаются, хранятся в репозитории и далее используются
* Читается markdown файл и разбирается на шаги
* Для каждого шага Step.to_dict записывается snapshot['steps'][i]['data']
Опция CLI -update или -u

Проверка dump:
* заранее вместе с эталонным снапшотом делается эталонный дамп и проверяется глазами/руками, заносится в репозиторий.
    examples/step1_markdown.md -> examples/step1_markdown_dump.md
    Лучше не глазами, а подменить lesson_id на другой урок (сделать специальный для отладки), deploy в этот урок
    и сравнить глазами исходный урок и этот отладочный, что форматирование не поплыло.
   CLI опиция -update_dump или -U
* проверка:
    * по указанному дампу маркдауна examples/step1_markdown_dump.md сделать еще один дамп,
    сохранить в src/verification/step1_markdown.md и сравнить diff.
"""


import json
import sys
from enum import StrEnum, IntEnum, auto, Enum
from pathlib import Path
from typing import Any
import click
from bs4 import BeautifulSoup

from src.lesson import Lesson
from src.settings import settings
from src.step import Step
from src.stepik_api import StepikSession
from src.utils import truncate, DEFAULT_MAX_LEN, context_diff_files
import src.export.dump as dump


class CompareError(Exception):
    pass

# Статусы
class StatusLesson(StrEnum):
    PASSED = "✅ "
    FAILED = "❌ "
    IN_PROGRESS = "In progress"

class StatusStep(StrEnum):
    PASSED = "✅ "
    FAILED = "❌ "
    SKIP = "➖ "
    REMOVE = "➖ "
    ADD = "➕ "


class Verbose(IntEnum):
    ERROR = auto()          # только сообщения об ошибках (в норме ничего)
    SUMMARY = auto()        # только информация pass/fail об уроке
    LESSON = auto()         # урок - количество шагов, из них .. pass, .. fail, .. skip.
    STEP = auto()           # по каждому шагу - pass, fail, skip, расхождение количества шагов, неожиданный skip
    DEBUG = auto()          # разница в полях dict шагов
    DUMP = auto()           # не обрезаем строки, в которых найдено различие, ставит SnapshotManager.truncate = False


class SnapshotAction(Enum):
    CREATE = auto()         # создание снапшота
    CHECK_MD2JSON = auto()  # проверка процесса "деплоя" - перевода из markdown в json
    CHECK_JSON2MD = auto()  # проверка процесса "дампа" - перевода из json в markdown

class SnapshotManager:
    LINE_LESSON_SEPARATOR = "=" * (DEFAULT_MAX_LEN // 2)
    LINE_STEP_SEPARATOR = "-" * (DEFAULT_MAX_LEN // 2)
    LINE_INTERSTEP_SEPARATOR = "." * (DEFAULT_MAX_LEN // 2)

    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    SNAPSHOTS_DIR = BASE_DIR / "src/verification/snapshots"
    SNAPSHOT_EXTENSION = ".json"
    MARKDOWN_TMP_DIR = BASE_DIR / "src/verification/tmp_markdown"  # src/verification/tmp_markdown
    MAX_TEXT_LINES_PREVIEW = 3
    SNAPSHOT_ACTION = "Используйте опцию -u для создания снапшота .json"
    DUMP_ACTION = "Используйте опцию -U для создания эталонного дамп файла .dump.md"

    def __init__(self, verbose: Verbose = Verbose.ERROR):
        self.snapshots_dir = Path(__file__).parent / self.SNAPSHOTS_DIR
        self.snapshots_dir.mkdir(exist_ok=True)
        self.__verbose: Verbose = verbose    # нужна ли подробная трассировка сравнения
        self.truncate: bool = True           # обрезать при выводе строки до ширины экрана

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
        snapshot_name = md_path.stem + self.SNAPSHOT_EXTENSION
        return self.snapshots_dir / snapshot_name

    @staticmethod
    def markdown_to_snapshot(md_text: str) -> dict:
        """Преобразует текст в формате markdown в словарь снапшота."""
        lesson = Lesson()

        lesson.parse_markdown(md_text)

        snapshot_data = {
            "metadata": {
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

        return snapshot_data

    def create_snapshot(self, md_filename: str | Path) -> str:
        """Создает/обновляет снапшот урока"""

        with open(md_filename, 'r', encoding='utf-8') as f:
            md_text = f.read()
            snapshot_data = self.markdown_to_snapshot(md_text=md_text)

        snapshot_path = self.get_snapshot_path(md_filename)
        with open(snapshot_path, 'w', encoding='utf-8') as file_out:
            json.dump(snapshot_data, file_out, indent=2, ensure_ascii=False)

        return f"Снапшот создан: {snapshot_path}"

    def load_snapshot(self, snapshot_path: str | Path) -> dict[str, Any]:
        """Возвращает снапшот в виде словаря из файла snapshot_path.
        :param snapshot_path: путь к файлу, из которого читается снапшот.
        :return:
        """
        try:
            snapshot_path = self.get_snapshot_path(snapshot_path)
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except OSError as e:
            raise CompareError(f"Ошибка доступа к файлу {e}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise CompareError(f"Ошибка загрузки снапшота {e}")

    def check_lesson_data(self,
                          expected_lesson: dict,
                          result_lesson: Lesson,
                          expected_filename: str | Path,
                          step_position: int = 0) -> StatusLesson:
        """Берет информацию об уроке из result_lesson и сравнивает ее и все шаги урока с expected_lesson.
        Если задан ненулевой step_position, сравнивается только указанный шаг.
        Имя исходного файла filename используется только для печати диагностики об ошибках.
        :param expected_lesson: - ожидаемое содержимое урока в виде словаря (из снапшота)
        :param result_lesson: - полученное содержимое урока в виде Lesson (у котрого будет to_dict())
        :param expected_filename:
        :param step_position: - для сравнения отдельного шага, нумерация с 1, по умолчанию 0 - все шаги.
        :return: результат сравнения урока в виде статуса (PASSED, FAILED)
        """

        markdown_steps = result_lesson.steps
        markdown_length = len(markdown_steps)
        snapshot_steps = expected_lesson["steps"]
        snapshot_length = len(snapshot_steps)
        step_position = result_lesson.make_position_positive(step_position=step_position)

        self.trace(Verbose.LESSON,
                   self.LINE_LESSON_SEPARATOR + '\n',
                   f"Урок DEPLOY {expected_filename}\n",
                   f"\t{snapshot_length} шагов - снапшот файл\n",
                   f"\t{markdown_length} шагов - markdown файл\n"
                   )

        step_results = []

        for position in range(1, 1 + max(markdown_length, snapshot_length)):
            # нужно разобрать только одну позицию, тогда остальные пропускаем

            if step_position and position != step_position:
                msg = f"\t{StatusStep.SKIP} Шаг {position}: пропускаем."
                self.trace(Verbose.STEP, msg)
                step_results.append(StatusStep.SKIP)
                # на всякий случай, если кто-то нарушит цепочку if..elif..else
                continue

            # в markdown шага нет, ошибка
            elif position > markdown_length:
                msg = f"\t{StatusStep.FAILED} Шаг {position} не существует. Всего шагов: {markdown_length}"
                self.trace(Verbose.STEP, msg)
                step_results.append(StatusStep.FAILED)

            # в снапшоте шага нет, ошибка
            elif position > snapshot_length:
                msg = f"\t{StatusStep.FAILED} Шаг {position} отсутствует в снапшоте. Всего шагов: {snapshot_length}"
                self.trace(Verbose.STEP, msg)
                step_results.append(StatusStep.FAILED)

            # пропускаем шаг в markdown (полезно, если он временно не работает и мы пометили его SKIP)
            elif markdown_steps[position - 1].skip:
                msg = f"\t{StatusStep.SKIP} шаг {position}: SKIP - пропускаем"
                self.trace(Verbose.STEP, msg)
                step_results.append(StatusStep.SKIP)

            # если шаг пропущен в снапшоте, но есть в markdown - ошибка
            # местами elif с предыдущим не менять!!!
            elif snapshot_steps[position - 1]['skip']:
                msg = f"\t{StatusStep.FAILED} Шаг {position} пропущен в снапшоте, но активен в текущем уроке"
                self.trace(Verbose.STEP, msg)
                step_results.append(StatusStep.FAILED)

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
        self.print_lesson_summary(result, expected_filename)
        return result['status']

    def check_lesson(self, markdown_filename: str | Path, step_position: int = 0) -> StatusLesson:
        """Проверяет урок из файла markdown_filename, сравнивая его с существующим снапшотом.
        Если задан step_position, то сравнивается только указанный шаг (нумерация с 1, может быть отрицательным).
        step_position = 0 - проверить весь урок.
        :param markdown_filename:
        :param step_position: - какой шаг сравнивать, 0 - все шаги (по умолчанию).
        :return: статус сравнения StatusLesson.PASSED или StatusLesson.FAILED
        """
        # Читаем снапшот из файла
        try:
            snapshot_path = self.get_snapshot_path(markdown_filename)
            snapshot = self.load_snapshot(snapshot_path)

            lesson = Lesson()
            with open(markdown_filename, 'r', encoding='utf-8') as f:
                lesson.parse_markdown(f.read(), step_position=step_position)

            return self.check_lesson_data(
                expected_lesson=snapshot,
                result_lesson=lesson,
                step_position=step_position,
                expected_filename=markdown_filename
            )

        except CompareError as e:
            self.trace(Verbose.ERROR, str(e))
            self.trace(Verbose.ERROR, self.SNAPSHOT_ACTION)
            return StatusLesson.FAILED

    @staticmethod
    def create_dump(src_path: str | Path, dst_path: str | Path, deploy: bool = False, new_step_begin: str | None = None) :
        """Из src_path в формате markdown делает dst_path в формате markdown с разделителем шагов new_step_begin.
        Это нужно, потому что степик режет часть информации (например, ширину колонок в таблице).
        Если deploy=True, то src_path деплоится на степик, иначе из файла берется lesson_id и делается дамп этого урока.
        :param src_path: - исходный markdown файл, по которому делается "стрипнутый" markdown
        :param dst_path: - результирующий markdown файл, после цепочки deploy + dump
        :param deploy: - надо ли реально деплоить на степик или возьмем то, что там уже лежит.
        :param new_step_begin: - разделитель шага при дампе; если None, берется из STEP_BEGIN настроек.

        """
        if new_step_begin is None:
            new_step_begin = settings.STEP_BEGIN

        # 1. Разбираем эталонный markdown из src_path
        lesson = Lesson()
        with open(src_path, 'r', encoding='utf-8') as f:
            lesson.parse_markdown(f.read())
        if deploy:
            lesson.deploy(StepikSession())

        lesson_id = lesson.lesson_id

        # 2. Делаем дамп этого урока c new_step_begin
        old_step_begin = settings.STEP_BEGIN
        settings.STEP_BEGIN = new_step_begin
        dump.dump_lesson(lesson_id=lesson_id, filename=dst_path)
        settings.STEP_BEGIN = old_step_begin


    def check_pulled_lesson_dump(self, markdown_filename: str | Path, step_position: int = 0) -> StatusLesson:
        """Проверяет урок из файла markdown_filename,
        * оттуда берем его lesson_id
        * dump этот урок в result_markdown_filename
        * сравниваем его с эталонным markdown_filename
        # Если задан step_position, то сравнивается только указанный шаг (нумерация с 1, может быть отрицательным).
        # step_position = 0 - проверить весь урок.
        """
        try:
            # Получаем пути к эталонному файлу и результирующему временному файлу дампов
            reference_markdown_path = self.md_dump_path(markdown_filename)
            if not reference_markdown_path.exists():
                self.trace(Verbose.ERROR, self.DUMP_ACTION)
                return StatusLesson.FAILED

            result_markdown_path = self.md_tmp_dump_path(markdown_filename)

            # 1. Добываем из эталонного маркдауна lesson_id
            lesson = Lesson()
            with open(reference_markdown_path, 'r', encoding='utf-8') as f:
                lesson.parse_markdown(f.read(), step_position=step_position)
            lesson_id = lesson.lesson_id

            # 2. Делаем дамп этого урока
            dump.dump_lesson(lesson_id=lesson_id, filename=result_markdown_path)

            # 3. diff reference_markdown_path result_markdown_path
            diff_text = context_diff_files(reference_markdown_path, result_markdown_path, context_line_number=0)
            if diff_text:
                self.trace(Verbose.LESSON, "DIFF: ")
                self.trace(Verbose.LESSON, diff_text)
                lesson_status = StatusLesson.FAILED
            else:
                lesson_status = StatusLesson.PASSED

            self.trace(Verbose.SUMMARY,
                       self.LINE_STEP_SEPARATOR,
                       f"{lesson_status}  Урок DUMP diff: {reference_markdown_path} vs {result_markdown_path}",
                       sep='\n',
                       end='\n'
                       )
            return lesson_status

        except CompareError as e:
            self.trace(Verbose.ERROR, str(e))
            self.trace(Verbose.ERROR, self.DUMP_ACTION)
            return StatusLesson.FAILED


    def compare_step(self, position: int, markdown_step: Step, snapshot_step: dict) -> StatusStep:
        """Сравнивает содержимое markdown_step.to_dict() и snapshot_step.
        Тип шага, заголовок, содержимое.
        Возвращает статус сравненного шага.
        :param position: номер шага, используется при печати диагностики
        :param markdown_step: разобранный markdown в виде Step
        :param snapshot_step: эталонный снапшот в виде dict
        :return: результат сравнения в виде статуса StatusStep
        """
        # не совпадает тип шага
        snapshot_step_type = snapshot_step["type"]
        markdown_step_type = markdown_step.__class__.__name__
        if snapshot_step_type != markdown_step_type:
            msg = f"\t{StatusStep.FAILED} Шаг {position}: изменился тип шага {snapshot_step_type} → {markdown_step_type}"
            self.trace(Verbose.STEP, msg)
            return StatusStep.FAILED

        # не совпадает заголовок шага
        if settings.STEP_BEGIN == settings.LEGACY_STEP_BEGIN:
            snapshot_step_header = snapshot_step["header"]
            markdown_step_header = markdown_step.header.strip()
            if snapshot_step_header != markdown_step_header:
                msg = f"\t{StatusStep.FAILED} Шаг {position}: изменился заголовок шага {snapshot_step_header} → {markdown_step_header}"
                self.trace(Verbose.STEP, msg)
                return StatusStep.FAILED

        # сравниваем данные
        snapshot_data = snapshot_step["data"]
        markdown_data = markdown_step.to_dict()

        # трассировка внутри сравнения
        msg = ""
        compare_result = self.compare_dict_as_json(snapshot_data, markdown_data)
        match compare_result:
            case StatusStep.PASSED:
                msg = f"\t{StatusStep.PASSED} Шаг {position}: ok"
            case StatusStep.FAILED:
                msg = f"\t{StatusStep.FAILED} Шаг {position}: обнаружены различия"
            case _:
                msg = f"\t Unexpected status {compare_result} сравнения шага {position}: ???"

        self.trace(Verbose.STEP, msg)
        return compare_result


    def compare_dict_as_json(self, markdown_dict: dict, snapshot_dict: dict) -> StatusStep:
        """Сравниваем словари рекурсивно до первой разницы или до конца, если разницы нет.
        Возвращает True, если словари одинаковые."""

        # отступ при печати трассировки
        indent = '\t\t'

        md_json = json.dumps(markdown_dict, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
        sn_json = json.dumps(snapshot_dict, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
        self.trace(Verbose.DEBUG, self.LINE_INTERSTEP_SEPARATOR)
        for md_line, sn_line in zip(md_json, sn_json):
            if md_line == sn_line:
                self.trace(Verbose.DEBUG, truncate(indent + md_line, ignore=self.truncate))
            else:
                self.trace(Verbose.DEBUG, truncate(indent + StatusStep.ADD +    " markdown: "+ md_line, ignore=self.truncate))
                self.trace(Verbose.DEBUG, truncate(indent + StatusStep.REMOVE + " snapshot: "+ sn_line, ignore=self.truncate))
                return StatusStep.FAILED

        return StatusStep.PASSED


    @staticmethod
    def total_results(step_results: list[StatusStep]) -> dict:
        """По статусам сравнения шагов вычисляем статус сравнения урока.
        Возвращаем статус сравнения урока вместе со статусами шагов."""
        totals = {
            "status": StatusLesson.IN_PROGRESS,
            "step_results": step_results,
            "steps_verified": 0,
            StatusStep.SKIP: 0,
            StatusStep.PASSED: 0,
            StatusStep.FAILED: 0,
        }

        totals['status'] = StatusLesson.PASSED
        for step_status in step_results:
            totals['steps_verified'] += 1
            totals[step_status] += 1
            if step_status is StatusStep.FAILED:
                totals['status'] = StatusLesson.FAILED

        return totals

    def print_lesson_summary(self, result: dict, filename: str | Path):
        """Трассировка итогов сравнения всех шагов урока."""

        self.trace(Verbose.SUMMARY,
                   self.LINE_STEP_SEPARATOR,
                   f"{result['status']}  Урок DEPLOY: {filename}",
                    f"\tВсего шагов: {result['steps_verified']}, из них",
                    f"\tPASS: {result[StatusStep.PASSED]}",
                    f"\tFAIL: {result[StatusStep.FAILED]}",
                    f"\tSKIP: {result[StatusStep.SKIP]}",
                   sep='\n',
                   end='\n'
                )

    @classmethod
    def md_tmp_dump_path(cls, path: str | Path) -> (Path, Path):
        """Из пути к исходному markdown файлу path получает путь к временному файлу с тем же именем.
        Если нужно, создает директорию."""
        tmp_dir = Path(__file__).parent / cls.MARKDOWN_TMP_DIR
        tmp_dir.resolve()
        if not tmp_dir.exists():
            tmp_dir.mkdir()
        filename = Path(path)
        return tmp_dir / filename.name

    @staticmethod
    def md_dump_path(markdown_filename: str | Path) -> Path:
        """По пути к исходному файлу примера возвращает путь к .dump.md файлу в той же директории.
        """
        base_path = Path.cwd()
        dump_filename = str(markdown_filename).replace(".md", ".dump.md")
        path = base_path / dump_filename
        return path.resolve()


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
              '(нумерация с 1, отрицательные - с конца, 0 - все шаги)')
@click.option('-u', '--update', is_flag=True, help='Обновить/создать снапшот')
@click.option('-U', '--update_dump', is_flag=True, help='Обновить/создать образец дампа урока')
@click.option('--dump', is_flag=True, help='Проверять дампа урока')
@click.option('-v', '--verbose',
              type=click.Choice(list(Verbose.__members__), case_sensitive=False),
              default='summary',
              help=verbose_help
)
@click.help_option('-h', '--help', help='Показать эту справку и выйти')
def main(filename: str, step: int, update: bool, update_dump: bool, dump: bool, verbose: str):
    """Менеджер снапшотов для верификации уроков Stepik"""

    manager = SnapshotManager()
    manager.verbose = verbose
    if verbose == Verbose.DUMP:
        manager.verbose = Verbose.DEBUG
        manager.truncate = False

    try:
        if update:
            # Создаем/обновляем снапшот
            result = manager.create_snapshot(filename)
            click.echo(result)
        if update_dump:
            md_dump_path = manager.md_dump_path(filename)
            manager.create_dump(src_path=filename, dst_path=md_dump_path, new_step_begin='---1234')

        if dump:
            # проверка дампа урока по эталонному дампу
            manager.trace(Verbose.LESSON, "--- DUMP --------------")
            settings.STEP_BEGIN = '---1234'
            # по lesson_id из исходного markdown_filename делаем dump урока во временную директорию
            # и сравниваем с эталонным дампом
            manager.check_pulled_lesson_dump(markdown_filename=filename, step_position=step)

        else:
            # TODO: тут должно быть запомнить старое значение и после проверок его восстановить, но зачем?
            settings.STEP_BEGIN = settings.LEGACY_STEP_BEGIN
            # проверяет исходный markdown файл и его преобразование в json, сравнивает с эталонным снапшотом
            manager.check_lesson(markdown_filename=filename, step_position=step)

    except Exception as e:
        click.echo(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

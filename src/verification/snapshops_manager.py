"""
Новый план проверки дампа:
* заранее вместе с эталонным снапшотом делается эталонный дамп и проверяется глазами/руками, заносится в репозиторий.
    examples/step1_markdown.md -> examples/step1_markdown_dump.md
* проверка:
    * по указанному дампу маркдауна examples/step1_markdown_dump.md сделать еще один дамп,
    сохранить в src/verification/step1_markdown.md и сравнить построчно.
    * проблема в SKIP шагах исходного макрдауна, если там реализованный тип шага и шаг сделан для эксперимента, то подумать, что будет сдамплено и как.



Проверка deploy: конвертация из markdown в body POST запросов для каждого шага.
* Исходный файл в формате markdown в директории examples, например markdown_file=examples/step_first.md
* Ему соответствует образец (snapshot) src/verification/step_first.json, свой формат json
* Читается markdown файл и разбирается на шаги
* Для каждого шага сравнивается Step.to_dict и snapshot['steps'][i]['data']

Подготовка образов (snapshot) - один раз создаются, хранятся в репозитории и далее используются
* Читается markdown файл и разбирается на шаги
* Для каждого шага Step.to_dict записывается snapshot['steps'][i]['data']
Опция CLI -update

Проверка dump:
* чтение snapshot файла
* Для каждого шага:
    * data = snapshot['steps'][i]['data']
    * конвертация из snapshot['steps'][i]['data'] в markdown
    * конвертация из markdown в result_data, используя Step.to_dict()
    * сравнение data и result_data
"""


import json
import sys
from enum import StrEnum, IntEnum, auto, Enum
from pathlib import Path
from typing import Any
import click
from bs4 import BeautifulSoup
import difflib

from src.lesson import Lesson
from src.settings import settings
from src.step import Step
from src.stepik_api import StepikSession
from src.utils import truncate, DEFAULT_MAX_LEN, context_diff_files
import src.export.dump as dump

SNAPSHOTS_DIR = "snapshots"
SNAPSHOT_EXTENSION = ".json"
MARKDOWN_TMP_DIR = "tmp_markdown"
MAX_TEXT_LINES_PREVIEW = 3
SNAPSHOT_ACTION = "Используйте опцию -u для создания снапшота"

class CompareError(Exception):
    pass

# Статусы
class StatusBase(StrEnum):
    PASSED = "✅ "
    EXPECTED_WARNING = "❕ "
    EXPECTED_FAILED = "‼️ "
    WARNING ="⚠️ "
    FAILED = "❌ "

StatusLesson = StrEnum(
    'StatusLesson',
    [(name, member.value) for name, member in StatusBase.__members__.items()] +
    [
        ('IN_PROGRESS', "In progress ")
    ]
)

StatusStep = StrEnum(
    'StatusLesson',
    [(name, member.value) for name, member in StatusBase.__members__.items()] +
    [
        ('SKIP', "➖ "),
        ('REMOVE', "➖ "),
        ('ADD', "➕ "),
    ]
)


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

    def __init__(self, verbose: Verbose = Verbose.ERROR):
        self.snapshots_dir = Path(__file__).parent / SNAPSHOTS_DIR
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
        snapshot_name = md_path.stem + SNAPSHOT_EXTENSION
        return self.snapshots_dir / snapshot_name

    def markdown_to_snapshot(self, md_text: str) -> dict:
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
        with open(snapshot_path, 'w', encoding='utf-8') as fout:
            json.dump(snapshot_data, fout, indent=2, ensure_ascii=False)

        return f"Снапшот создан: {snapshot_path}"

    def load_snapshot(self, md_filename: str) -> dict[str, Any]:
        """Загружает снапшот из файла.
        Если md_filename имеет расширение .md, то это markdown файл, по которому надо найти файл со снапшотом."""
        snapshot_path = md_filename
        try:
            path = Path(md_filename)

            if Path(md_filename).with_suffix(".md"):
                snapshot_path = self.get_snapshot_path(md_filename)
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except OSError as e:
            raise CompareError(f"Ошибка доступа к файлу {e}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise CompareError(f"Ошибка загрузки снапшота {e}")

    def check_lesson_data(self,
                          expected_lesson: dict,
                          result_lesson: Lesson,
                          expected_filename: str,
                          step_position: int = 0,
                          mode: str = 'DEPLOY') -> StatusLesson:
        """Берет информацию об уроке из result_lesson и сравнивает ее и все шаги урока с expected_lesson.
        Если задан ненулевой step_position, сравнивается только указанный шаг.
        Имя исходного файла filename используется только для печати диагностики об ошибках.
        """

        markdown_steps = result_lesson.steps
        markdown_length = len(markdown_steps)
        snapshot_steps = expected_lesson["steps"]
        snapshot_length = len(snapshot_steps)
        step_position = result_lesson.make_position_positive(step_position=step_position)

        self.trace(Verbose.LESSON,
                   self.LINE_LESSON_SEPARATOR + '\n',
                   f"Урок {mode} {expected_filename}\n",
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
        self.print_lesson_summary(result, expected_filename, mode)
        return result['status']

    def check_lesson(self, markdown_filename: str | Path, step_position: int = 0) -> StatusLesson:
        """Проверяет урок из файла markdown_filename, сравнивая его с существующим снапшотом.
        Если задан step_position, то сравнивается только указанный шаг (нумерация с 1, может быть отрицательным).
        step_position = 0 - проверить весь урок.
        """
        # Читаем снапшот из файла
        try:
            snapshot = self.load_snapshot(markdown_filename)

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
            self.trace(Verbose.ERROR, SNAPSHOT_ACTION)
            return StatusLesson.FAILED

    def check_pulled_lesson_dump_old(self, markdown_filename: str | Path, step_position: int = 0) -> StatusLesson:
        """Проверяет урок из файла markdown_filename,
        * по файлу идем в его снапшот
        * оттуда берем его lesson_id
        * скачиваем информацию об уроке + ВСЕ шаги и преобразуем ее в markdown (resulted_markdown_path)
        * из markdown делаем snapshot (result_snapshot_path)
        * сравнивая его с существующим снапшотом
        Если задан step_position, то сравнивается только указанный шаг (нумерация с 1, может быть отрицательным).
        step_position = 0 - проверить весь урок.
        """

        # Читаем снапшот из файла
        try:
            snapshot = self.load_snapshot(markdown_filename)
            lesson_id = snapshot["metadata"]["lesson_id"]

            result_markdown_path, result_snapshot_path = self.make_tmp_paths(markdown_filename)

            # # теперь все снапшоты будут записываться сюда
            # tmp_dir = Path(__file__).parent / "tmp_markdown"
            # markdown_name = Path(markdown_filename).name
            # # куда будем класть полученные markdown и snapshot файлы из скаченных
            # result_markdown_path = tmp_dir / markdown_name
            # result_snapshot_path = result_markdown_path.with_suffix(".json")

            dump.dump_lesson(lesson_id=lesson_id, filename=result_markdown_path)
            self.snapshots_dir = result_markdown_path.parent
            self.create_snapshot(result_markdown_path)

            step_results = []
            with open(result_snapshot_path, "r", encoding="utf8") as result_fin:
                result_snapshot = json.load(result_fin)
                print(f"{len(snapshot["steps"])=}")
                print(f"{len(result_snapshot["steps"])=}")
                for position, snapshot_step in enumerate(snapshot["steps"]):
                    if step_position and position != step_position:
                        msg = f"\t{StatusStep.SKIP} Шаг {position+1}: пропускаем."
                        self.trace(Verbose.STEP, msg)
                        step_results.append(StatusStep.SKIP)
                        # на всякий случай, если кто-то нарушит цепочку if..elif..else
                        continue

                    result_snapshot_step = result_snapshot["steps"][position]
                    result = self.compare_step_snapshots(
                        snapshot_step_result=result_snapshot_step,
                        snapshot_step=snapshot_step,
                        position=position+1)
                    step_results.append(result)

                # по статусам сравнения шагов вычисляем статус сравнения урока
                result = self.total_results(step_results)
                self.print_lesson_summary(result, markdown_filename, 'DUMP')
                return result["status"]

        except CompareError as e:
            self.trace(Verbose.ERROR, str(e))
            self.trace(Verbose.ERROR, SNAPSHOT_ACTION)
            return StatusLesson.FAILED

    def create_dump(self, src_path: str | Path, dst_path: str | Path, deploy: bool = False, new_step_begin: str='---1234') :
        """Из src_path в формате markdown делает dst_path в формате markdown с разделителем шагов new_step_begin.
        Если deploy=True, то src_path деплоится на степик, иначе из файла берется lesson_id и делается дамп этого урока.
        """
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


    def check_pulled_lesson_dump(self, markdown_filename: str, step_position: int = 0) -> StatusLesson:
        """Проверяет урок из файла markdown_filename,
        * оттуда берем его lesson_id
        * dump этот урок в result_markdown_filename
        * сравниваем его с эталонным markdown_filename
        # Если задан step_position, то сравнивается только указанный шаг (нумерация с 1, может быть отрицательным).
        # step_position = 0 - проверить весь урок.
        """
        # Получаем пути к эталонному файлу и результирующему временному файлу дампов
        reference_markdown_path = self.md_dump_path(markdown_filename)

        result_markdown_path = Path(__file__).parent / "tmp_markdown/step1_markdown.md"
        # TODO: проверяем существование нужных файлов

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
                   f"{lesson_status}  Урок DUMP: {reference_markdown_path}",
                   sep='\n',
                   end='\n'
                   )
        return lesson_status


    def compare_step(self, position: int, markdown_step: Step, snapshot_step: dict) -> StatusStep:
        """Сравнивает содержимое markdown_step.to_dict() и snapshot_step.
        Тип шага, заголовок, содержимое.
        Возвращает статус сравненного шага.
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
        match(compare_result):
            case StatusStep.PASSED:
                msg = f"\t{StatusStep.PASSED} Шаг {position}: ok"
            # case StatusStep.WARNING:
            #     msg = f"\t{StatusStep.WARNING} Шаг {position}: HTML warning"
            case StatusStep.FAILED:
                msg = f"\t{StatusStep.FAILED} Шаг {position}: обнаружены различия"
            case _:
                msg = f"\t Unexpected status {compare_result} сравнения шага {position}: ???"

        self.trace(Verbose.STEP, msg)
        return compare_result


    def compare_step_snapshots(self, position: int, snapshot_step_result: dict, snapshot_step: dict) -> StatusStep:
        """Сравнивает содержимое snapshot_step_result и snapshot_step.
        Тип шага, заголовок, содержимое.
        Возвращает статус сравненного шага.
        """
        # не совпадает тип шага
        snapshot_step_type = snapshot_step["type"]
        result_step_type = snapshot_step_result["type"]
        if snapshot_step_type != result_step_type:
            msg = f"\t{StatusStep.FAILED} Шаг {position}: изменился тип шага {snapshot_step_type} → {result_step_type}"
            self.trace(Verbose.STEP, msg)
            return StatusStep.FAILED

        # не совпадает заголовок шага - не проверяем!

        # сравниваем данные
        snapshot_data = snapshot_step["data"]
        result_data = snapshot_step_result["data"]

        # трассировка внутри сравнения
        compare_result = self.compare_dict_as_json(snapshot_data, result_data, skip_problem_html_tags=True)
        match compare_result:
            case StatusStep.PASSED:
                msg = f"\t{StatusStep.PASSED} Шаг {position}: ok"
            case StatusStep.WARNING:
                msg = f"\t{StatusStep.WARNING} Шаг {position}: HTML warning"
            case StatusStep.FAILED:
                msg = f"\t{StatusStep.FAILED} Шаг {position}: обнаружены различия"
            case _:
                msg = f"\t Unexpected status {compare_result} сравнения шага {position}: ???"

        self.trace(Verbose.STEP, msg)
        return compare_result

    @classmethod
    def remove_problem_html_tags(cls, text) -> str:
        """
        Используется для сравнения html кода
        :param text:
        :return:
        """
        # если это вообще не HTML, ничего не меняем
        if not ("<" in text and ">" in text):
            return text
        soup = BeautifulSoup(text, 'html.parser')
        result = soup.get_text()
        return result

    def compare_dict_as_json(self, markdown_dict: dict, snapshot_dict: dict, skip_problem_html_tags: bool = False) -> StatusStep:
        """Сравниваем словари рекурсивно до первой разницы или до конца, если разницы нет.
        Возвращает True, если словари одинаковые."""

        # отступ при печати трассировки
        indent = '\t\t'

        md_json = json.dumps(markdown_dict, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
        sn_json = json.dumps(snapshot_dict, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
        self.trace(Verbose.DEBUG, self.LINE_INTERSTEP_SEPARATOR)
        has_warning_line = False
        for md_line, sn_line in zip(md_json, sn_json):
            if md_line == sn_line:
                self.trace(Verbose.DEBUG, truncate(indent + md_line, ignore=self.truncate))
            else:
                self.trace(Verbose.DEBUG, truncate(indent + StatusStep.ADD +    " markdown: "+ md_line, ignore=self.truncate))
                self.trace(Verbose.DEBUG, truncate(indent + StatusStep.REMOVE + " snapshot: "+ sn_line, ignore=self.truncate))
                md_line_no_html = self.remove_problem_html_tags(md_line)
                sn_line_no_html = self.remove_problem_html_tags(sn_line)
                print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print(f"{md_line_no_html=}")
                print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print(f"{sn_line_no_html=}")
                print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print(f"{skip_problem_html_tags=} + {md_line_no_html == sn_line_no_html}")
                if skip_problem_html_tags and md_line_no_html == sn_line_no_html:
                    self.trace(Verbose.DEBUG,
                               truncate(indent + StatusStep.WARNING + " strip: " + md_line, ignore=self.truncate))
                    has_warning_line = True
                else:
                    return StatusStep.FAILED

        return StatusStep.WARNING if has_warning_line else StatusStep.PASSED

    @staticmethod
    def total_results(step_results: list[StatusStep]) -> dict:
        """По статусам сравнения шагов вычисляем статус сравнения урока.
        Возвращаем статус сравнения урока вместе со статусами шагов."""
        totals = {
            "status": StatusLesson.IN_PROGRESS,
            "step_results": step_results,
            "steps_verified": 0,
            str(StatusStep.SKIP): 0    # потому что не входит в StatusBase, потому что не может быть статусом урока
        }
        # статус всего урока - самый последний из встреченных статусов
        for step_status in StatusBase:
            totals[str(step_status)] = 0
            if step_status in step_results:
                totals['status'] = step_status

        for step_status in step_results:
            totals['steps_verified'] += 1
            totals[str(step_status)] += 1

        return totals

    def print_lesson_summary(self, result: dict, filename: str | Path, mode: str):
        """Трассировка итогов сравнения всех шагов урока."""

        self.trace(Verbose.SUMMARY,
                   self.LINE_STEP_SEPARATOR,
                   f"{result['status']}  Урок {mode.upper()}: {filename}",
                    f"\tВсего шагов: {result['steps_verified']}, из них",
                    f"\tPASS: {result[StatusBase.PASSED]}",
                    f"\tWARN: {result[StatusBase.WARNING]}",
                    f"\tFAIL: {result[StatusBase.FAILED]}",
                    f"\tSKIP: {result[StatusStep.SKIP]}",
                   sep='\n',
                   end='\n'
                )

    def make_tmp_paths(self, path: str | Path) -> (Path, Path):
        """Из пути к исходному markdown файлу path получает путь к временному файлу с тем же именем.
        Если нужно, создает директорию."""
        tmp_dir = Path(__file__).parent / MARKDOWN_TMP_DIR
        tmp_dir.resolve()
        if not tmp_dir.exists():
            tmp_dir.mkdir()
        filename = Path(path)
        return tmp_dir / filename.name, tmp_dir / filename.with_suffix(".json").name

    def md_dump_path(self, markdown_filename: str) -> Path:
        """По пути к исходному файлу примера возвращает путь к .dump.md файлу в той же директории.
        """
        base_path = Path.cwd()
        dump_filename = markdown_filename.replace(".md", ".dump.md")
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
@click.option('-v', '--verbose',
              type=click.Choice(list(Verbose.__members__), case_sensitive=False),
              default='summary',
              help=verbose_help
)
@click.help_option('-h', '--help', help='Показать эту справку и выйти')
def main(filename: str, step: int, update: bool, update_dump: bool, verbose: str):
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
            result = manager.create_dump(src_path=filename, dst_path=md_dump_path, new_step_begin='---1234')
            click.echo(result)
        else:
            # TODO: тут должно быть запомнить старое значение и после проверок его восстановить, но зачем?
            settings.STEP_BEGIN = settings.LEGACY_STEP_BEGIN
            # проверяет исходный markdown файл и его преобразование в json, сравнивает с эталонным снапшотом
            manager.check_lesson(markdown_filename=filename, step_position=step)
            manager.trace(Verbose.LESSON, "--- DUMP --------------")
            settings.STEP_BEGIN = '---1234'
            # по lesson_id из исходного markdown_filename делаем dump урока во временную директорию
            # и сравниваем с эталонным дампом
            manager.check_pulled_lesson_dump(markdown_filename=filename, step_position=step)

    except Exception as e:
        click.echo(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

    # manager = SnapshotManager()
    # manager.verbose = Verbose.DEBUG
    # result = manager.check_pulled_lesson_dump(markdown_filename="filename")
    # print(result)

    # for status in StatusLesson:
    #     print(status)
    # print(StatusLesson, type(StatusLesson))
    # print(StatusLesson.IN_PROGRESS)
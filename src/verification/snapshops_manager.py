import json
import sys
from pathlib import Path
from typing import Any
import click

from src.lesson import Lesson
from src.step import Step

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class SnapshotManager:
    def __init__(self):
        self.snapshots_dir = Path(__file__).parent / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

    def get_snapshot_path(self, md_filename: str) -> Path:
        """Получает путь к файлу снапшота на основе MD файла"""
        md_path = Path(md_filename)
        snapshot_name = md_path.stem + ".json"
        return self.snapshots_dir / snapshot_name

    def create_snapshot(self, md_filename: str) -> str:
        """Создает/обновляет снапшот урока"""

        lesson = Lesson()

        with open(md_filename, 'r', encoding='utf-8') as f:
            lesson.parse_markdown(f.read())

        # Фильтруем шаги, исключая пропущенные
        non_skipped_steps = [step for step in lesson.steps if not step.skip]

        snapshot_data = {
            "metadata": {
                "source_md": md_filename,
                "total_steps": len(non_skipped_steps),
                "lesson_id": lesson.lesson_id,
                "title": lesson.title
            },
            "steps": []
        }

        for i, step in enumerate(non_skipped_steps):
            step_data = step.to_dict()

            snapshot_step = {
                "position": i + 1,
                "type": step.__class__.__name__,
                "header": step.header.strip(),
                "data": step_data
            }
            snapshot_data["steps"].append(snapshot_step)

        snapshot_path = self.get_snapshot_path(md_filename)
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

        return f"Снапшот создан: {snapshot_path}"

    def load_snapshot(self, md_filename: str) -> dict[str, Any]:
        """Загружает снапшот из файла"""
        snapshot_path = self.get_snapshot_path(md_filename)
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Снапшот не найден: {snapshot_path}")

        with open(snapshot_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def verify_lesson(self, lesson: Lesson, md_filename: str) -> dict[str, Any]:
        """Проверяет весь урок: текущий lesson со снапшотом в md_filename"""
        try:
            snapshot = self.load_snapshot(md_filename)
        except FileNotFoundError as e:
            return {
                "status": "error",
                "message": str(e),
                "action": "Используйте опцию -u для создания снапшота"
            }

        results = {
            "status": "success",
            "lesson": md_filename,
            "steps_verified": 0,
            "steps_passed": 0,
            "steps_failed": 0,
            "step_results": []
        }

        current_steps = [step for step in lesson.steps if not step.skip]
        print(
            f"Проверка снапшота ({len(snapshot['steps'])} шагов)",
            f"vs текущего урока ({len(current_steps)} шагов)")

        max_steps = max(len(snapshot["steps"]), len(current_steps))

        for position in range(1, max_steps + 1):
            snapshot_step = None
            current_step = None

            print(f"  Позиция {position}:")
            if position <= len(snapshot["steps"]):
                snapshot_step = snapshot["steps"][position - 1]
                print(f"    Снапшот: {snapshot_step['header']}")
            if position <= len(current_steps):
                current_step = current_steps[position - 1]
                print(f"    Текущий: {current_step.header}")

            step_result = self._compare_steps(
                position, snapshot_step, current_step)
            results["step_results"].append(step_result)
            results["steps_verified"] += 1

            if step_result["status"] == "passed":
                results["steps_passed"] += 1
            elif step_result["status"] in ["failed", "extra_in_snapshot", "new_in_current"]:
                results["steps_failed"] += 1

        return results

    def _compare_steps(self, position: int, snapshot_step: dict | None, current_step: Step | None) -> dict[str, Any]:
        """Сравнивает шаги по позиции"""
        # Шаг есть только в снапшоте
        if snapshot_step and not current_step:
            return {
                "position": position,
                "header": snapshot_step["header"],
                "status": "extra_in_snapshot",
                "message": "Шаг есть в снапшоте, но отсутствует в текущем уроке"
            }

        # Шаг есть только в текущем уроке
        if not snapshot_step and current_step:
            return {
                "position": position,
                "header": current_step.header,
                "status": "new_in_current",
                "message": "Новый шаг в текущем уроке, отсутствует в снапшоте"
            }

        # Оба шага существуют - сравниваем их
        # Проверяем тип шага
        if snapshot_step["type"] != current_step.__class__.__name__:
            return {
                "position": position,
                "header": snapshot_step["header"],
                "status": "failed",
                "message": f"Тип шага изменился: {snapshot_step['type']} → {current_step.__class__.__name__}"
            }

        # Проверяем заголовок (дополнительная проверка)
        header_match = snapshot_step["header"] == current_step.header.strip()
        if not header_match:
            return {
                "position": position,
                "header": f"{snapshot_step['header']} → {current_step.header}",
                "status": "failed",
                "message": f"Заголовок изменился: '{snapshot_step['header']}' → '{current_step.header}'"
            }

        # Сравниваем данные
        snapshot_data = snapshot_step["data"]
        current_data = current_step.to_dict()

        differences = self._compare_dicts(snapshot_data, current_data)

        if not differences:
            return {
                "position": position,
                "header": snapshot_step["header"],
                "type": snapshot_step["type"],
                "status": "passed",
                "message": "Шаг соответствует снапшоту"
            }
        else:
            return {
                "position": position,
                "header": snapshot_step["header"],
                "type": snapshot_step["type"],
                "status": "failed",
                "message": "Обнаружены различия",
                "differences": differences
            }

    def verify_single_step(self, md_filename: str, step_position: int) -> dict[str, Any]:
        """Проверяет один конкретный шаг"""

        lesson = Lesson()

        with open(md_filename, 'r', encoding='utf-8') as f:
            lesson.parse_markdown(f.read())

        try:
            snapshot = self.load_snapshot(md_filename)
        except FileNotFoundError as e:
            return {
                "status": "error",
                "message": str(e),
                "action": "Используйте опцию -u для создания снапшота"
            }

        # Фильтруем шаги, исключая пропущенные
        current_steps = [step for step in lesson.steps if not step.skip]

        # Нормализуем позицию (поддержка отрицательных номеров)
        total_steps = len(snapshot["steps"])
        if step_position < 0:
            step_position = total_steps + step_position + 1

        if step_position < 1 or step_position > total_steps:
            return {
                "status": "error",
                "message": f"Шаг {step_position} не существует. Всего шагов: {total_steps}"
            }

        if step_position > len(current_steps):
            return {
                "status": "error",
                "message": f"Шаг {step_position} отсутствует в текущем уроке"
            }

        snapshot_step = snapshot["steps"][step_position - 1]
        current_step = current_steps[step_position - 1]

        return self._compare_steps(step_position, snapshot_step, current_step)

    def _normalize_test_cases(self, test_cases):
        """Нормализует формат тестовых случаев для сравнения"""
        if not isinstance(test_cases, list):
            return test_cases

        normalized = []
        for case in test_cases:
            if isinstance(case, (list, tuple)):
                # Конвертируем в кортеж для единообразия
                normalized.append(tuple(case))
            else:
                normalized.append(case)
        return normalized

    def _compare_dicts(self, dict1: dict, dict2: dict, path: str = "") -> list[str]:
        """Рекурсивно сравнивает два словаря и возвращает список различий"""
        differences = []

        all_keys = set(dict1.keys()) | set(dict2.keys())

        for key in all_keys:
            current_path = f"{path}.{key}" if path else key

            if key not in dict1:
                differences.append(
                    f"➕ Добавлено поле: {current_path} = {
                        self._truncate_value(dict2[key])}")
            elif key not in dict2:
                differences.append(
                    f"➖ Удалено поле: {current_path} = {
                        self._truncate_value(dict1[key])}")
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # Рекурсивное сравнение вложенных словарей
                nested_diffs = self._compare_dicts(
                    dict1[key], dict2[key], current_path)
                differences.extend(nested_diffs)
            else:
                # Специальная обработка для test_cases
                if current_path.endswith("test_cases"):
                    normalized1 = self._normalize_test_cases(dict1[key])
                    normalized2 = self._normalize_test_cases(dict2[key])
                    if normalized1 != normalized2:
                        differences.append(
                            f"Изменено поле: {current_path}\n"
                            f"   Было: {self._truncate_value(dict1[key])}\n"
                            f"   Стало: {self._truncate_value(dict2[key])}")
                elif dict1[key] != dict2[key]:
                    # Сравнение для текстовых полей
                    if key == "text" or "text" in current_path:
                        old_lines = str(dict1[key]).split('\n')
                        new_lines = str(dict2[key]).split('\n')

                        if len(old_lines) > 3 or len(new_lines) > 3:
                            differences.append(
                                f"Изменен текст: {current_path}\n"
                                f"  Было ({len(old_lines)} строк):\n      "
                                + "\n    ".join(old_lines[:3])
                                + ("\n    ..." if len(old_lines) > 3 else ""))

                            differences.append(
                                f"  Стало ({len(new_lines)} строк):\n      "
                                + "\n    ".join(new_lines[:3])
                                + ("\n   ..." if len(new_lines) > 3 else ""))
                        else:
                            differences.append(
                                f"Изменено поле: {current_path}\n"
                                f"  Было: {self._truncate_value(dict1[key])}\n"
                                f"  Стало: {self._truncate_value(dict2[key])}")
                    else:
                        differences.append(
                            f"Изменено поле: {current_path}\n"
                            f"  Было: {self._truncate_value(dict1[key])}\n"
                            f"  Стало: {self._truncate_value(dict2[key])}")

        return differences

    def _truncate_value(self, value: Any, max_length: int = 100) -> str:
        """Обрезает длинные значения для читаемости"""
        if isinstance(value, str) and len(value) > max_length:
            return value[:max_length] + "..."
        return str(value)


def _print_step_result(result: dict):
    """Выводит результат проверки одного шага"""
    position = result["position"]
    header = result["header"]

    if result["status"] == "passed":
        click.echo(f"✅ Шаг {position}: {header} - СООТВЕТСТВУЕТ")

    elif result["status"] == "extra_in_snapshot":
        click.echo(f"Шаг {position}: {header} - ЕСТЬ В СНАПШОТЕ, НЕТ В УРОКЕ")

    elif result["status"] == "new_in_current":
        click.echo(f"Шаг {position}: {header} - НОВЫЙ ШАГ, НЕТ В СНАПШОТЕ")

    elif result["status"] == "failed":
        click.echo(f"❌ Шаг {position}: {header} - ОШИБКИ")
        if "type" in result:
            click.echo(f"   Тип: {result['type']}")
        click.echo(f"   Причина: {result['message']}")

        if "differences" in result:
            for diff in result["differences"]:
                formatted_diff = diff.replace('\n', '\n      ')
                click.echo(f"   {formatted_diff}")


def _print_lesson_result(result: dict):
    """Выводит результат проверки всего урока"""
    click.echo(f"Урок: {result['lesson']}")

    if result.get("status") == "warning" and "message" in result:
        click.echo(f"⚠️  {result['message']}")

    click.echo(f"Проверено шагов: {result['steps_verified']}")
    click.echo(f"✅ Пройдено: {result['steps_passed']}")
    click.echo(f"❌ Ошибок: {result['steps_failed']}")
    click.echo("")

    for step_result in result["step_results"]:
        _print_step_result(step_result)

    if result["steps_failed"] == 0:
        click.echo("\nВсе шаги соответствуют снапшоту!")
    else:
        click.echo(f"\nНайдено {result['steps_failed']} несоответствий")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('filename', type=click.Path(exists=True), required=False)
@click.option('-s', '--step', type=int, default=0, metavar='STEP',
              help='Сверить только конкретный шаг '
              '(нумерация с 1, отрицательные - с конца)')
@click.option('-u', '--update', is_flag=True, help='Обновить/создать снапшот')
@click.help_option('-h', '--help', help='Показать эту справку и выйти')
def main(filename: str, step: int, update: bool):
    """Менеджер снапшотов для верификации уроков Stepik"""

    manager = SnapshotManager()

    if (filename is None):
        print("Необходимо указать файл", file=sys.stderr)
        sys.exit(1)

    try:
        if update:
            # Создаем/обновляем снапшот
            result = manager.create_snapshot(filename)
            click.echo(result)

        elif step != 0:
            # Проверяем один шаг
            result = manager.verify_single_step(filename, step)

            if result["status"] == "error":
                click.echo(f"❌ Ошибка: {result['message']}")
                if "action" in result:
                    click.echo(f"{result['action']}")
            else:
                _print_step_result(result)

        else:
            # Парсим урок из MD файла
            lesson = Lesson()

            with open(filename, 'r', encoding='utf-8') as f:
                lesson.parse_markdown(f.read())

            # Проверяем весь урок
            result = manager.verify_lesson(lesson, filename)

            if result["status"] == "error":
                click.echo(f"❌ Ошибка: {result['message']}")
                if "action" in result:
                    click.echo(f"{result['action']}")
            else:
                _print_lesson_result(result)

    except Exception as e:
        click.echo(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

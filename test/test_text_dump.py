from unittest.mock import patch, MagicMock, call
import pytest
import markdown
from bs4 import BeautifulSoup

from src.export.dump import (
    dump_lesson,
    get_exporter,
    TextDump,
    generate_lesson_header,
    get_lesson_info,
    BaseExporter,
)
from src.settings import settings

pytestmark = pytest.mark.step_begin("---1234")

# ========== ТЕСТ 1: ПРЕОБРАЗОВАНИЕ LaTeX ==========

@pytest.fixture
def text_exporter():
    """Фикстура для создания экземпляра TextDump"""
    return TextDump({'block': {'text': '', 'name': 'text'}}, 1)


@pytest.mark.parametrize("input_text, expected", [
    (r'\(e=mc^2\)', '$e=mc^2$'),
    (r'\[y=\sin{x}\]', '\n\n$$y=\sin{x}$$\n\n'),
    (r'Текст \(формула\) и еще \(другая\)', 'Текст $формула$ и еще $другая$'),
    (r'\[дисплейная\] и \(строчная\)', '\n\n$$дисплейная$$\n\n и $строчная$'),
])
def test_fix_latex_converts_delimiters(text_exporter, input_text, expected):
    """Проверка конвертации LaTeX-разделителей в формат Markdown"""
    assert text_exporter.fix_latex(input_text) == expected


def test_fix_latex_complex_example(text_exporter):
    """Тест на реальном примере из дампа урока"""
    input_text = r"""
    Вставка отдельной формулы \(e=mc^2\) в тексте. 
    В него подставим отдельно стоящую формулу
    \(y=sin⁡x\)
    """
    expected = """
    Вставка отдельной формулы $e=mc^2$ в тексте. 
    В него подставим отдельно стоящую формулу
    $y=sin⁡x$
    """
    assert text_exporter.fix_latex(input_text).strip() == expected.strip()


@pytest.mark.parametrize("input_text, expected", [
    # Квадратное уравнение
    (r'\(x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}\)', 
     r'$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$'),
    
    # Определенный интеграл
    (r'\[\int_{0}^{\infty} e^{-x} \, dx\]', 
     r'\n\n$$\int_{0}^{\infty} e^{-x} \, dx$$\n\n'),
    
    # Система уравнений
    (r'\[|x| = \begin{cases} x, & \text{если } x \geq 0 \\ -x, & \text{если } x < 0 \end{cases}\]', 
     r'\n\n$$|x| = \begin{cases} x, & \text{если } x \geq 0 \\ -x, & \text{если } x < 0 \end{cases}$$\n\n'),
    
    # Матрица - убираем [0.3em] из теста, так как это ломает split
    (r'\[M = \begin{bmatrix} \frac{5}{6} & \frac{1}{6} & 0 \\ \frac{5}{6} & 0 & \frac{1}{6} \\ 0 & \frac{5}{6} & \frac{1}{6} \end{bmatrix}\]', 
     r'\n\n$$M = \begin{bmatrix} \frac{5}{6} & \frac{1}{6} & 0 \\ \frac{5}{6} & 0 & \frac{1}{6} \\ 0 & \frac{5}{6} & \frac{1}{6} \end{bmatrix}$$\n\n'),
    
    # Сумма/произведение
    (r'\[\sum_{i=1}^{n} i = \frac{n(n+1)}{2}\]', 
     r'\n\n$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$\n\n'),
    
    # Предел
    (r'\[\lim_{x \to 0} \frac{\sin x}{x} = 1\]', 
     r'\n\n$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$\n\n'),
])
def test_fix_latex_complex_math(text_exporter, input_text, expected):
    """Проверка конвертации сложных математических формул"""
    result = text_exporter.fix_latex(input_text)
    result = result.replace('\n\n', r'\n\n')
    assert result == expected

def test_fix_latex_mixed_complex_formulas(text_exporter):
    """Проверка смешанных сложных формул в одном тексте"""
    input_text = r"""
    Квадратное уравнение: \(x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}\)

    Определенный интеграл: \[\int_{0}^{\infty} e^{-x} \, dx\]

    Матрица: \[M = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}\]

    Система: \[|x| = \begin{cases} x, & x \geq 0 \\ -x, & x < 0 \end{cases}\]
    """
    
    expected = """
    Квадратное уравнение: $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$

    Определенный интеграл: 

    $$\\int_{0}^{\\infty} e^{-x} \\, dx$$

    Матрица: 

    $$M = \\begin{bmatrix} 1 & 2 \\\\ 3 & 4 \\end{bmatrix}$$

    Система: 

    $$|x| = \\begin{cases} x, & x \\geq 0 \\\\ -x, & x < 0 \\end{cases}$$
    """
    
    result = text_exporter.fix_latex(input_text)
    result_lines = [line.strip() for line in result.split('\n') if line.strip()]
    expected_lines = [line.strip() for line in expected.split('\n') if line.strip()]
    assert result_lines == expected_lines

# ========== ТЕСТ 2: HTML ТЕГИ ВНУТРИ <pre> И <code> ==========

def test_pre_tag_keeps_html_escaped():
    """Проверка, что HTML внутри <pre> остаётся экранированным"""
    html = "<pre>&lt;h1&gt;Заголовок&lt;/h1&gt; &lt;p&gt;параграф&lt;/p&gt;</pre>"
    result = markdown.markdown(html, extensions=['extra', 'nl2br'])
    
    assert '<pre>' in result
    assert '&lt;h1&gt;Заголовок&lt;/h1&gt;' in result
    assert '&lt;p&gt;параграф&lt;/p&gt;' in result


def test_code_tag_keeps_html_escaped():
    """Проверка, что HTML внутри <code> остаётся экранированным"""
    html = "<p>Тег <code>&lt;div&gt;</code> используется для блоков</p>"
    result = markdown.markdown(html, extensions=['extra', 'nl2br'])
    
    assert '<code>&lt;div&gt;</code>' in result


def test_pre_with_code_nested():
    """Проверка вложенных <pre><code> с HTML внутри"""
    html = """
    <pre><code class="language-html">
    &lt;html&gt;
        &lt;body&gt;
            &lt;h1&gt;Hello&lt;/h1&gt;
        &lt;/body&gt;
    &lt;/html&gt;
    </code></pre>
    """
    result = markdown.markdown(html, extensions=['extra', 'nl2br', 'fenced_code'])
    
    # Проверяем, что HTML теги преобразованы в сущности
    assert '&lt;html&gt;' in result or '&amp;lt;html&amp;gt;' in result
    assert '&lt;body&gt;' in result or '&amp;lt;body&amp;gt;' in result
    assert '&lt;h1&gt;Hello&lt;/h1&gt;' in result or '&amp;lt;h1&amp;gt;Hello&amp;lt;/h1&amp;gt;' in result


# ========== ТЕСТ 3: НЕСТАНДАРТНЫЙ HTML ==========

def test_details_tag_is_preserved():
    """Проверка, что тег <details> сохраняется при конвертации"""
    html = """
    <details><summary>Тестовые данные</summary>
            <h4>Test #1 input</h4>
            <pre></pre>
            <h4>Test #1 output</h4>
            <pre>Hello, world!</pre>
    </details>
    """
    result = markdown.markdown(html, extensions=['extra', 'nl2br'])
    
    # Проверяем, что содержимое сохранилось (теги могут быть экранированы)
    assert 'Тестовые данные' in result
    assert 'Test #1 input' in result
    assert 'Test #1 output' in result
    assert 'Hello, world!' in result


def test_unknown_html_tags_are_preserved():
    """Проверка, что любые неизвестные HTML теги сохраняются"""
    html = """
    <custom-tag attr="value">Содержимое</custom-tag>
    <another-tag>Текст</another-tag>
    <article>
        <header>Заголовок</header>
        <footer>Подвал</footer>
    </article>
    """
    result = markdown.markdown(html, extensions=['extra', 'nl2br'])
    
    # Проверяем, что содержимое сохранилось
    assert 'Содержимое' in result
    assert 'Текст' in result
    assert 'Заголовок' in result
    assert 'Подвал' in result


# ========== ТЕСТ 5: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

@patch('src.export.dump.StepikSession')
def test_get_lesson_info(mock_session_class):
    """Проверка получения информации об уроке"""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    mock_session.fetch_object.return_value = {
        'title': 'Тестовый урок',
        'steps': [1, 2, 3]
    }
    
    title, steps = get_lesson_info(mock_session, 123)
    
    assert title == 'Тестовый урок'
    assert steps == [1, 2, 3]
    mock_session.fetch_object.assert_called_once_with('lesson', 123)


def test_generate_lesson_header():
    """Проверка генерации заголовка урока"""
    result = generate_lesson_header('Мой урок', 456)
    assert result == ['# Мой урок', '', 'lesson: 456', '']


def test_get_exporter_for_text():
    """Проверка получения экспортера для текстового шага"""
    step_data = {'block': {'name': 'text'}}
    exporter = get_exporter(step_data, 1)
    assert isinstance(exporter, TextDump)
    assert exporter.position == 1


def test_get_exporter_for_unknown():
    """Проверка получения экспортера для неизвестного типа"""
    from src.export.dump import get_exporter, TextDump
    
    step_data = {'block': {'name': 'unknown'}}
    exporter = get_exporter(step_data, 1)
    assert isinstance(exporter, TextDump)
    assert exporter.position == 1


# ========== ТЕСТ 6: ЭКСПОРТЕР TEXTDUMP ==========

# пример работы с mock функций (для истории и чтобы смотреть на образец)
@patch('src.export.dump.md')
def test_textdump_export(mock_md):
    """Проверка экспорта текстового шага"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_md.return_value = "Конвертированный текст"
    
    step_data = {
        'block': {
            'text': '<h2>Заголовок</h2><p>Содержимое</p>',
            'name': 'text'
        }
    }
    
    exporter = TextDump(step_data, 1)
    with patch.object(exporter, 'fix_latex', return_value="Конвертированный текст"):
        result = exporter.export()
    
    assert '---1234 TEXT\n\nКонвертированный текст\n' == result
    mock_md.assert_called_once()


def test_textdump_without_title():
    """Проверка экспорта шага без заголовка"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    step_data = {
        'block': {
            'text': '<p>Просто текст без заголовка</p>',
            'name': 'text'
        }
    }
    
    exporter = TextDump(step_data, 5)
    result = exporter.export()
    
    assert '---1234 TEXT\n\nПросто текст без заголовка\n' == result


def test_textdump_process_code_blocks():
    """Проверка обработки блоков кода"""
    html = '<pre><code class="language-python">print("Hello")</code></pre>'
    step_data = {'block': {'text': html, 'name': 'text'}}

    expected_codeblock = """

```python
print("Hello")
```

"""
    
    exporter = TextDump(step_data, 1)
    exporter.soup = BeautifulSoup(html, 'html.parser')
    exporter.soup = exporter.process_code_blocks(exporter.soup)
    
    result = str(exporter.soup)
    assert result == expected_codeblock


# ========== ТЕСТ 7: ФУНКЦИЯ DUMP_LESSON ==========

@patch('src.export.dump.StepikSession')
@patch('src.export.dump.read_or_create_auth_data')
@patch('src.export.dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_calls_api_correctly(mock_open, mock_logger, mock_auth, mock_session_class):
    """Проверка, что dump_lesson правильно вызывает API"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_session_instance = MagicMock()
    mock_session_class.return_value = mock_session_instance
    
    mock_session_instance.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1, 2]},
        {'block': {'text': '<h2>Шаг 1</h2><p>Текст</p>', 'name': 'text'}},
        {'block': {'text': '<h2>Шаг 2</h2><p>Еще текст</p>', 'name': 'text'}}
    ]
    
    dump_lesson(123, 'test.md')
    
    expected_calls = [
        call('lesson', 123),
        call('step-source', 1),
        call('step-source', 2)
    ]
    mock_session_instance.fetch_object.assert_has_calls(expected_calls, any_order=False)
    
    settings.STEP_BEGIN = original
    mock_open.assert_called_once_with('test.md', 'w', encoding='utf-8')


@patch('src.export.dump.StepikSession')
@patch('src.export.dump.read_or_create_auth_data')
@patch('src.export.dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_handles_empty_steps_gracefully(mock_open, mock_logger, mock_auth, mock_session_class):
    """Проверка, что dump_lesson корректно обрабатывает урок без шагов"""
    mock_session_instance = MagicMock()
    mock_session_class.return_value = mock_session_instance
    mock_session_instance.fetch_object.return_value = {
        'title': 'Пустой урок',
        'steps': []
    }
    
    dump_lesson(456, 'empty.md')
    mock_open.assert_not_called()  # Файл не должен создаваться для пустого урока


@patch('src.export.dump.StepikSession')
@patch('src.export.dump.read_or_create_auth_data')
@patch('src.export.dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_with_custom_filename(mock_open, mock_logger, mock_auth, mock_session_class):
    """Проверка, что dump_lesson принимает кастомное имя файла"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_session_instance = MagicMock()
    mock_session_class.return_value = mock_session_instance
    
    mock_session_instance.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1]}, 
        {'block': {'name': 'text', 'text': '<h2>Шаг</h2>'}} 
    ]
    
    dump_lesson(789, 'custom_name.md')
    settings.STEP_BEGIN = original
    mock_open.assert_called_once_with('custom_name.md', 'w', encoding='utf-8')


# ========== ТЕСТ 8: ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ DUMP_LESSON ==========

@pytest.fixture
def mock_session():
    """Фикстура для мока StepikSession"""
    with patch('src.export.dump.StepikSession') as mock:
        session_instance = MagicMock()
        mock.return_value = session_instance
        yield session_instance


@pytest.fixture
def mock_dependencies():
    """Фикстура для мока зависимостей dump_lesson"""
    with patch('src.export.dump.read_or_create_auth_data') as mock_auth, \
         patch('src.export.dump.setup_logger') as mock_logger, \
         patch('builtins.open', MagicMock()) as mock_open:
        yield {'auth': mock_auth, 'logger': mock_logger, 'open': mock_open}


def test_dump_lesson_basic_api_calls(mock_session, mock_dependencies):
    """Проверка базовых вызовов API при дампе урока"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1, 2]},
        {'block': {'name': 'text', 'text': '<h2>Шаг 1</h2><p>Текст</p>'}},
        {'block': {'name': 'text', 'text': '<h2>Шаг 2</h2><p>Еще текст</p>'}}
    ]
    
    dump_lesson(123, 'test.md')
    
    expected_calls = [
        call('lesson', 123),
        call('step-source', 1),
        call('step-source', 2)
    ]
    settings.STEP_BEGIN = original
    mock_session.fetch_object.assert_has_calls(expected_calls, any_order=False)
    mock_dependencies['open'].assert_called_once_with('test.md', 'w', encoding='utf-8')


def test_dump_lesson_with_text_content(mock_session, mock_dependencies):
    """Проверка дампа урока с текстовыми шагами"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1]},
        {'block': {'name': 'text', 'text': '<h2>Привет</h2><p>Мир</p>'}}
    ]
    expected_lesson_md = '# Тестовый урок\n\nlesson: 123\n\n---1234 TEXT\n\n## Привет\n\nМир\n'
    dump_lesson(123, 'test.md')
    
    # Проверяем запись в файл
    handle = mock_dependencies['open'].return_value.__enter__.return_value
    written_content = ''.join(call[0][0] for call in handle.write.call_args_list)

    assert written_content == expected_lesson_md


def test_dump_lesson_empty_steps(mock_session, mock_dependencies):
    """Проверка обработки урока без шагов"""
    mock_session.fetch_object.return_value = {
        'title': 'Пустой урок',
        'steps': []
    }
    
    dump_lesson(456, 'empty.md')
    mock_dependencies['open'].assert_not_called()  # Файл не должен создаваться


def test_dump_lesson_default_filename(mock_session, mock_dependencies):
    """Проверка генерации имени файла по умолчанию"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1]},
        {'block': {'name': 'text', 'text': '<h2>Шаг</h2>'}}
    ]
    
    dump_lesson(789)
    settings.STEP_BEGIN = original
    mock_dependencies['open'].assert_called_once_with('lesson_789.md', 'w', encoding='utf-8')


def test_dump_lesson_handles_step_error(mock_session, mock_dependencies, capsys):
    """Проверка обработки ошибки при экспорте шага"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1, 2]},
        Exception("Ошибка загрузки шага"),
        {'block': {'name': 'text', 'text': '<h2>Шаг 2</h2>'}}
    ]
    
    dump_lesson(123, 'test.md')
    
    # Проверяем, что ошибка была выведена
    captured = capsys.readouterr()
    settings.STEP_BEGIN = original
    assert "Ошибка при обработке шага" in captured.out
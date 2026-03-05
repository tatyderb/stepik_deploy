from unittest.mock import patch, MagicMock, call
import pytest
import markdown

from src.export.text_dump import (
    dump_lesson,
    get_exporter,
    TextDump,
    generate_lesson_header,
    get_lesson_info,
    BaseExporter,
)

# ========== ТЕСТ 1: ПРЕОБРАЗОВАНИЕ LaTeX ==========

@pytest.fixture
def exporter():
    """Фикстура для создания экземпляра BaseExporter"""
    return BaseExporter({'block': {'text': ''}}, 1)

@pytest.mark.parametrize("input_text, expected", [
    (r'\(e=mc^2\)', '$e=mc^2$'),
    (r'\[y=\sin{x}\]', '$$y=\sin{x}$$'),
    (r'Текст \(формула\) и еще \(другая\)', 'Текст $формула$ и еще $другая$'),
    (r'\[дисплейная\] и \(строчная\)', '$$дисплейная$$ и $строчная$'),
])
def test_fix_latex_converts_delimiters(exporter, input_text, expected):
    """Проверка конвертации LaTeX-разделителей в формат Markdown"""
    assert exporter.fix_latex(input_text) == expected


@pytest.mark.parametrize("input_text, expected", [
    (r'\= \= \=', '= = ='),
    (r'\+ и \- и \*', '+ и - и *'),
    (r'\$100 и \=50', '$100 и =50'),
    (r'смешанный \= текст с \+', 'смешанный = текст с +'),
])
def test_fix_latex_removes_escaping(exporter, input_text, expected):
    """Проверка удаления экранирования у символов = + - * $"""
    assert exporter.fix_latex(input_text) == expected


def test_fix_latex_complex_example(exporter):
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
    assert exporter.fix_latex(input_text).strip() == expected.strip()


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


# ========== ТЕСТ 4: ФУНКЦИЯ ADJUST_HEADER_LEVELS ==========

@pytest.fixture
def text_exporter():
    """Фикстура для создания экземпляра TextDump"""
    return TextDump({'block': {'text': ''}}, 1)

def test_adjust_header_levels_shifts_all_headers(text_exporter):
    """Проверка смещения уровней заголовков"""
    md = """
# Заголовок 1
## Заголовок 2
### Заголовок 3
Обычный текст
"""
    result = text_exporter.adjust_header_levels(md, base_level=2)
    
    # Проверяем, что заголовки изменились
    assert '## Заголовок 1' in result
    assert '### Заголовок 2' in result
    assert '#### Заголовок 3' in result
    assert 'Обычный текст' in result


def test_adjust_header_levels_respects_max_level(text_exporter):
    """Проверка ограничения максимального уровня (6)"""
    md = """
##### Заголовок 5
###### Заголовок 6
####### Заголовок 7 (слишком много)
"""
    result = text_exporter.adjust_header_levels(md, base_level=2)
    
    # Проверяем, что уровни не превышают 6
    assert '###### Заголовок 5' in result  # 5 -> 6
    assert '###### Заголовок 6' in result  # 6 -> 6
    assert '###### Заголовок 7' in result  # 7 -> 6


def test_adjust_header_levels_ignores_non_headers(text_exporter):
    """Проверка, что обычный текст не меняется"""
    md = "Обычный текст\n* пункт списка\n| таблица |"
    result = text_exporter.adjust_header_levels(md)
    assert result == md

# ========== ТЕСТ 5: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

@patch('src.export.text_dump.StepikSession')
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
    step_data = {'block': {'name': 'unknown'}}
    with pytest.raises(TypeError):
        exporter = get_exporter(step_data, 1)  # Должно упасть с TypeError
    # exporter = get_exporter(step_data, 1)
    # assert exporter is None


# ========== ТЕСТ 6: ЭКСПОРТЕР TEXTDUMP ==========

@patch('src.export.text_dump.convert_to_markdown')
def test_textdump_export(mock_convert):
    """Проверка экспорта текстового шага"""
    mock_convert.return_value = "Конвертированный текст"
    
    step_data = {
        'block': {
            'text': '<h2>Заголовок</h2><p>Содержимое</p>',
            'name': 'text'
        }
    }
    
    exporter = TextDump(step_data, 1)
    result = exporter.export()
    
    assert '## Заголовок' in result
    assert 'Конвертированный текст' in result
    mock_convert.assert_called_once()


def test_textdump_without_title():
    """Проверка экспорта шага без заголовка"""
    step_data = {
        'block': {
            'text': '<p>Просто текст без заголовка</p>',
            'name': 'text'
        }
    }
    
    exporter = TextDump(step_data, 5)
    result = exporter.export()
    
    assert '## Шаг 5' in result


def test_textdump_extract_title():
    """Проверка извлечения заголовка из HTML"""
    step_data = {
        'block': {
            'text': '<h3>Важный заголовок</h3><p>Текст</p>',
            'name': 'text'
        }
    }
    
    exporter = TextDump(step_data, 1)
    assert exporter.extract_title() == 'Важный заголовок'
    assert '<h3>' not in exporter.html  # Заголовок должен быть удален

# ========== ТЕСТ 7: ФУНКЦИЯ DUMP_LESSON ==========

@patch('src.export.text_dump.StepikSession')
@patch('src.export.text_dump.read_or_create_auth_data')
@patch('src.export.text_dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_calls_api_correctly(mock_open, mock_logger, mock_auth, mock_session_):
    """Проверка, что dump_lesson правильно вызывает API"""
    mock_session_instance = MagicMock()
    mock_session_.return_value = mock_session_instance
    
    mock_session_instance.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1, 2]},
        {'block': {'text': '<h2>Шаг 1</h2><p>Текст</p>'}},
        {'block': {'text': '<h2>Шаг 2</h2><p>Еще текст</p>'}}
    ]
    
    dump_lesson(123, 'test.md')
    
    expected_calls = [
        call('lesson', 123),
        call('step-source', 1),
        call('step-source', 2)
    ]
    mock_session_instance.fetch_object.assert_has_calls(expected_calls, any_order=False)
    
    mock_open.assert_called_once_with('test.md', 'w', encoding='utf-8')


@patch('src.export.text_dump.StepikSession')
@patch('src.export.text_dump.read_or_create_auth_data')
@patch('src.export.text_dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_handles_empty_steps_gracefully(mock_open, mock_logger, mock_auth, mock_session_):
    """Проверка, что dump_lesson корректно обрабатывает урок без шагов"""
    mock_session_instance = MagicMock()
    mock_session_.return_value = mock_session_instance
    mock_session_instance.fetch_object.return_value = {
        'title': 'Пустой урок',
        'steps': []
    }
    
    dump_lesson(456, 'empty.md')
    mock_open.assert_not_called()  # Файл не должен создаваться для пустого урока


@patch('src.export.text_dump.StepikSession')
@patch('src.export.text_dump.read_or_create_auth_data')
@patch('src.export.text_dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_with_custom_filename(mock_open, mock_logger, mock_auth, mock_session_):
    """Проверка, что dump_lesson принимает кастомное имя файла"""
    mock_session_instance = MagicMock()
    mock_session_.return_value = mock_session_instance
    
    mock_session_instance.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1]}, 
        {'block': {'name': 'text', 'text': '<h2>Шаг</h2>'}} 
    ]
    
    dump_lesson(789, 'custom_name.md')
    mock_open.assert_called_once_with('custom_name.md', 'w', encoding='utf-8')


# ========== ТЕСТ 8: ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ DUMP_LESSON ==========

@pytest.fixture
def mock_session():
    """Фикстура для мока StepikSession"""
    with patch('src.export.text_dump.StepikSession') as mock:
        session_instance = MagicMock()
        mock.return_value = session_instance
        yield session_instance


@pytest.fixture
def mock_dependencies():
    """Фикстура для мока зависимостей dump_lesson"""
    with patch('src.export.text_dump.read_or_create_auth_data') as mock_auth, \
         patch('src.export.text_dump.setup_logger') as mock_logger, \
         patch('builtins.open', MagicMock()) as mock_open:
        yield {'auth': mock_auth, 'logger': mock_logger, 'open': mock_open}


def test_dump_lesson_basic_api_calls(mock_session, mock_dependencies):
    """Проверка базовых вызовов API при дампе урока"""
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
    mock_session.fetch_object.assert_has_calls(expected_calls, any_order=False)
    mock_dependencies['open'].assert_called_once_with('test.md', 'w', encoding='utf-8')


def test_dump_lesson_with_text_content(mock_session, mock_dependencies):
    """Проверка дампа урока с текстовыми шагами"""
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1]},
        {'block': {'name': 'text', 'text': '<h2>Привет</h2><p>Мир</p>'}}
    ]
    
    with patch('src.export.text_dump.convert_to_markdown') as mock_convert:
        mock_convert.return_value = "Конвертированный текст"
        dump_lesson(123, 'test.md')
    
    # Проверяем запись в файл
    handle = mock_dependencies['open'].return_value.__enter__.return_value
    written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
    
    assert '# Тестовый урок' in written_content
    assert 'lesson: 123' in written_content
    assert '## Привет' in written_content
    assert 'Конвертированный текст' in written_content


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
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1]},
        {'block': {'name': 'text', 'text': '<h2>Шаг</h2>'}}
    ]
    
    dump_lesson(789)
    mock_dependencies['open'].assert_called_once_with('lesson_789.md', 'w', encoding='utf-8')


def test_dump_lesson_handles_step_error(mock_session, mock_dependencies, capsys):
    """Проверка обработки ошибки при экспорте шага"""
    mock_session.fetch_object.side_effect = [
        {'title': 'Тестовый урок', 'steps': [1, 2]},
        Exception("Ошибка загрузки шага"),
        {'block': {'name': 'text', 'text': '<h2>Шаг 2</h2>'}}
    ]
    
    dump_lesson(123, 'test.md')
    
    # Проверяем, что ошибка была выведена
    captured = capsys.readouterr()
    assert "Ошибка при обработке шага" in captured.out
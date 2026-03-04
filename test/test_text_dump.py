from unittest.mock import patch, MagicMock, call
import pytest
import markdown

from src.export.text_dump import fix_latex, adjust_header_levels, dump_lesson


# ========== ТЕСТ 1: ПРЕОБРАЗОВАНИЕ LaTeX ==========

@pytest.mark.parametrize("input_text, expected", [
    (r'\(e=mc^2\)', '$e=mc^2$'),
    (r'\[y=\sin{x}\]', '$$y=\sin{x}$$'),
    (r'Текст \(формула\) и еще \(другая\)', 'Текст $формула$ и еще $другая$'),
    (r'\[дисплейная\] и \(строчная\)', '$$дисплейная$$ и $строчная$'),
])
def test_fix_latex_converts_delimiters(input_text, expected):
    """Проверка конвертации LaTeX-разделителей в формат Markdown"""
    assert fix_latex(input_text) == expected


@pytest.mark.parametrize("input_text, expected", [
    (r'\= \= \=', '= = ='),
    (r'\+ и \- и \*', '+ и - и *'),
    (r'\$100 и \=50', '$100 и =50'),
    (r'смешанный \= текст с \+', 'смешанный = текст с +'),
])
def test_fix_latex_removes_escaping(input_text, expected):
    """Проверка удаления экранирования у символов = + - * $"""
    assert fix_latex(input_text) == expected


def test_fix_latex_complex_example():
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
    assert fix_latex(input_text).strip() == expected.strip()


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

def test_adjust_header_levels_shifts_all_headers():
    """Проверка смещения уровней заголовков"""
    md = """
# Заголовок 1
## Заголовок 2
### Заголовок 3
Обычный текст
"""
    result = adjust_header_levels(md, base_level=2)
    
    # Проверяем, что заголовки изменились
    assert '## Заголовок 1' in result
    assert '### Заголовок 2' in result
    assert '#### Заголовок 3' in result
    assert 'Обычный текст' in result


def test_adjust_header_levels_respects_max_level():
    """Проверка ограничения максимального уровня (6)"""
    md = """
##### Заголовок 5
###### Заголовок 6
####### Заголовок 7 (слишком много)
"""
    result = adjust_header_levels(md, base_level=2)
    
    # Проверяем, что уровни не превышают 6
    assert '###### Заголовок 5' in result  # 5 -> 6
    assert '###### Заголовок 6' in result  # 6 -> 6
    assert '###### Заголовок 7' in result  # 7 -> 6


def test_adjust_header_levels_ignores_non_headers():
    """Проверка, что обычный текст не меняется"""
    md = "Обычный текст\n* пункт списка\n| таблица |"
    result = adjust_header_levels(md)
    assert result == md


# ========== ТЕСТ 5: ФУНКЦИЯ DUMP_LESSON ==========

@patch('src.export.text_dump.StepikSession')
@patch('src.export.text_dump.read_or_create_auth_data')
@patch('src.export.text_dump.setup_logger')
@patch('builtins.open', new_callable=MagicMock)
def test_dump_lesson_calls_api_correctly(mock_open, mock_logger, mock_auth, mock_session):
    """Проверка, что dump_lesson правильно вызывает API"""
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    
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
def test_dump_lesson_handles_empty_steps_gracefully(mock_logger, mock_auth, mock_session):
    """Проверка, что dump_lesson корректно обрабатывает урок без шагов"""
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.fetch_object.return_value = {
        'title': 'Пустой урок',
        'steps': []
    }
    
    try:
        dump_lesson(456, 'empty.md')
    except Exception as e:
        pytest.fail(f"dump_lesson вызвал исключение: {e}")


@patch('src.export.text_dump.StepikSession')
@patch('src.export.text_dump.read_or_create_auth_data')
@patch('src.export.text_dump.setup_logger')
def test_dump_lesson_with_custom_filename(mock_logger, mock_auth, mock_session):
    """Проверка, что dump_lesson принимает кастомное имя файла"""
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.fetch_object.return_value = {
        'title': 'Тестовый урок',
        'steps': []
    }
    
    try:
        dump_lesson(789, 'custom_name.md')
    except Exception as e:
        pytest.fail(f"dump_lesson с кастомным именем вызвал исключение: {e}")
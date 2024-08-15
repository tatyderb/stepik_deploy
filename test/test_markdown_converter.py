from src.utils import markdown_to_html

text = '''
# Заголовок первого уровня

Нормальный текст.

*Курсив* $c^2 = a^2 + b%2$ и **жирный**.

* пункт 1
* пункт 2
* пункт 3 и `дополнение`

```python
x, y = map(int, input().split())
print(x + y)
```
    Конец.
    '''

html_text = '''<h1>Заголовок первого уровня</h1>
<p>Нормальный текст.</p>
<p><em>Курсив</em> $c^2 = a^2 + b%2$ и <strong>жирный</strong>.</p>
<ul>
<li>пункт 1</li>
<li>пункт 2</li>
<li>пункт 3 и <code>дополнение</code></li>
</ul>
<pre><code class="language-python">x, y = map(int, input().split())
print(x + y)
</code></pre>
<pre><code>Конец.
</code></pre>'''


def test_markdown_to_html():
    res = markdown_to_html(text)
    # print(res)
    assert res == html_text

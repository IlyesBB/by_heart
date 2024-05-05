from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.lexers.dax import DaxLexer
from pygments.formatters import HtmlFormatter

if __name__ == '__main__':
    code = [
        'import pandas as pd',
        'import numpy as np',
        'def myfunc():',
        '\tprint(3)'
    ]
    code = '\n'.join(code)
    print(highlight(code, PythonLexer(), HtmlFormatter()))
    print()
    print(HtmlFormatter().get_style_defs('.highlight'))
    print()
    print(get_lexer_by_name('html'))

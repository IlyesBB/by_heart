import bs4.element

from learn.deck import FlashCard
from jinja2 import Environment, FileSystemLoader
import latex2mathml.converter
import re
from config import templates_directory
import os
from gui.deck import write_flashcard_css
from bs4 import BeautifulSoup
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight



write_flashcard_css()

"""
Contains functions to generate HTML string to display flashcards.
Use generate_card_html(...) to generate the HTML content.
"""

environment = Environment(loader=FileSystemLoader(templates_directory))
template = environment.get_template("flashcard.html")


def generate_card_html(card: FlashCard, face: str = 'both') -> str:
    """
    Creates the HTML string for a flashcard.

    If face = 'front', only shows the question
    If face = 'back', only shows the response
    Else, shows both question and response

    The HTML is built with the template flashcard.html in templates_directory (config.py). Corresponding stylesheet is
    flashcard.css file in the same directory.

    Question and response are wrapped in HTML div tags, and can contain HTML elements, and some of their content is
    parsed by function format_content.

    @param card: Flashcard to generate HTML for
    @param face: Can have 'front', 'back' or other values
    @return: HTML string of the Flashcard
    """
    display_question = 'none' if face == 'back' else 'block'
    display_correction = 'none' if face == 'front' else 'block'
    content = template.render(question=format_content(card.question),
                              correction=format_content(card.correction),
                              display_question=display_question,
                              display_correction=display_correction,
                              css_file_path=os.path.join(templates_directory, "flashcard.css"))
    return content


def format_content(html) -> str:
    """
    Replaces Latex expressions between $$ and lines beginning with 'file:///', using the functions:
    - latex_to_mathml
    - replace_img_paths
    @param html: HTML file in string format
    @return: HTML string with MathML formulas and HTML img tags
    """
    html = latex_to_mathml(html)
    html = replace_img_paths(html)
    html = replace_code(html)
    return html


def latex_to_mathml(html: str) -> str:
    """
    Replaces Latex expressions between $$ with the corresponding MathML expression
    @param html: HTML file in string format
    @return: HTML string with Latex formulas turned to MathML
    """
    html_split = html.split('$$')
    for ind, chunk in enumerate(html_split):
        if ind % 2 == 1:
            html_split[ind] = latex2mathml.converter.convert(chunk)
    return ''.join(html_split)


def replace_img_paths(html: str) -> str:
    """
    Replaces the lines beginning with 'file:///[Image path]' by the corresponding HTML img tag
    @param html: HTML file in string format
    @return: HTML string with the appropriate img tags
    """
    return re.sub("file:///(.+)(\n|$)", r'<img src="\1">', html)


def replace_code(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.findAll(re.compile(".+-code"))
    tags: [bs4.element.Tag]
    for tag in tags:
        language = tag.name.split('-')[0]
        lexer = get_lexer_by_name(language)
        res = highlight(tag.text, lexer, HtmlFormatter())
        tag.replaceWith(BeautifulSoup(res, "html.parser"))
    return str(soup)


if __name__ == '__main__':

    html_ = [
        '<python-code>',
        'def myfunc():',
        '\t' + 'print(1)',
        '</python-code>',
        '<dax-code>',
        'CALENDARAUTO()',
        '</dax-code>'
    ]
    html_ = '\n'.join(html_)
    print(replace_code(html_))


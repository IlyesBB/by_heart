from config import templates_directory
import os
from pygments.formatters import HtmlFormatter

start_css = """
#question {
    font-size: 22px;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 5px 5px 5px grey;
    margin-top: 30px;
    background: rgba(0,0,255,0.1);
}

#correction {
    font-size: 22px;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 5px 5px 5px grey;
    margin-top: 20px;
    background: rgba(255,255,0,0.5);
}
"""


def write_flashcard_css():
    with open(os.path.join(templates_directory, 'flashcard.css'), 'w') as file:
        file.write(start_css + HtmlFormatter().get_style_defs('.highlight'))


if __name__ == '__main__':
    write_flashcard_css()

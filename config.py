from datetime import timedelta
import os

project_directory = os.path.dirname(__file__)

if not os.path.isdir(os.path.join(project_directory, 'data')):
    os.mkdir(os.path.join(project_directory, 'data'))

decks_directory = os.path.join(project_directory, 'data', 'decks')
records_directory = os.path.join(project_directory, 'data', 'records')
picker_directory = os.path.join(project_directory, 'data', 'picker')

for directory in [decks_directory, records_directory, picker_directory]:
    if not os.path.isdir(directory):
        os.mkdir(directory)

icons_directory = os.path.join(project_directory, 'images', 'icons')

templates_directory = os.path.join(project_directory, 'gui', 'templates')

intervals = [
    timedelta(minutes=15),
    timedelta(hours=1),
    timedelta(days=1),
    timedelta(days=2),
    timedelta(days=3),
    timedelta(weeks=1),
    timedelta(weeks=2),
    timedelta(weeks=3),
    timedelta(weeks=4),
    timedelta(weeks=4),
    timedelta(weeks=4),
    timedelta(weeks=8),
    timedelta(weeks=8),
    timedelta(weeks=16),
    timedelta(weeks=24),
    timedelta(weeks=56)
]

sample_size = 3
warmup_size = 2
factor_max = 1.5

from datetime import timedelta
import os

# project_directory: Root path of the project
project_directory = os.path.dirname(__file__)

# data_directory: Directory is created to store user flashcard related data
data_directory = os.path.join(project_directory, 'data')
if not os.path.isdir(data_directory):
    os.mkdir(data_directory)

# decks_directory: Directory containing one deck file per user deck
decks_directory = os.path.join(project_directory, 'data', 'decks')
# records_directory: Directory containing one records file per user deck
records_directory = os.path.join(project_directory, 'data', 'records')
# picker_directory: Directory containing one file for target times and one for interval boxes per user deck
picker_directory = os.path.join(project_directory, 'data', 'picker')

# Creating the needed directories if not already existing
for directory in [decks_directory, records_directory, picker_directory]:
    if not os.path.isdir(directory):
        os.mkdir(directory)

# icons_directory: Directory containing the icons used by the app
icons_directory = os.path.join(project_directory, 'images', 'icons')

# templates_directory: Directory containing the html and css files for the app
templates_directory = os.path.join(project_directory, 'gui', 'templates')

# intervals: Flashcard review intervals
intervals = [
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

# sample_size: Number of records to determine target response time for a flashcard
sample_size = 3
# warmup_size: Number of records before starting to record target time
warmup_size = 2
# factor_max: Factor between target response time and admissible response time
factor_max = 1.5

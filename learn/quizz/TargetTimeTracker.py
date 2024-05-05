from learn.deck import Deck, FlashCard
from config import picker_directory
import os
import json
from typing import Dict


class TargetTimeTracker:
    """
    Manages flashcard target response times.

    Response time for a flashcard is defined as the minimal time in seconds to write the answer the flashcard.
    This class allows to get and set the target time of a flashcard:
    - get_target_time(...)
    - set_target_time(...)

    Flashcard-target time associations are saved as json dictionaries, with the .ttm extension, in the picker_directory
    (defined in config.py)
    """
    def __init__(self, deck: Deck):
        self.deck = deck
        # target_time: Dictionary between flashcard key and target time in seconds
        self.target_time: Dict[str, float] = self.read_target_times(self.deck)

    def get_target_time(self, card: FlashCard) -> float | None:
        """
        @param card: Flashcard for which to get the target duration
        @return: Target time in seconds, or none
        """
        if card.key in self.target_time.keys():
            return self.target_time[card.key]

    def set_target_time(self, card: FlashCard, target_time: float | None) -> None:
        """
        @param card: Flashcard for which to get the target duration
        @param target_time: Target time in seconds, or none
        """
        self.target_time[card.key] = round(target_time, 1) if isinstance(target_time, float) else target_time

    def save(self):
        """
        Saves the flashcards' target times to the picker_directory (defined in config.py) with the .ttm extension.
        """
        with open(os.path.join(picker_directory, self.deck.key + '.ttm'), 'w') as file:
            json.dump(self.target_time, file)

    @staticmethod
    def read_target_times(deck: Deck) -> Dict[str, float]:
        """
        @param deck: Deck for which reading the target times
        Reads the flashcards' target times from the picker_directory (defined in config.py) with the .ttm extension.
        """
        file_path = os.path.join(picker_directory, deck.key + '.ttm')
        if not os.path.isfile(file_path):
            return {}
        with open(file_path, 'r') as file:
            return json.load(file)

    def delete(self):
        """
        Deletes the flashcards' target times from the picker_directory (defined in config.py) with the .ttm extension.
        """
        file_path = os.path.join(picker_directory, self.deck.key + '.ttm')
        if os.path.isfile(file_path):
            os.remove(file_path)

    def remove_card(self, card: FlashCard):
        self.remove_cards([card])

    def remove_cards(self, cards: [FlashCard]):
        for card in cards:
            if card.key in self.target_time.keys():
                del self.target_time[card.key]

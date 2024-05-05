from learn.deck import Deck, FlashCard
from config import picker_directory, intervals
import os
import json
from typing import Dict
from datetime import timedelta


class Scheduler:
    """
    Manages flashcard boxes and repetition intervals to implement Leitner system.

    Flashcards are in boxes, to which are associated repetition intervals.
    This class allows to move a flashcard to the next/previous/first box, with the following methods:
    - next_box(...)
    - previous_box(...)
    - reset_box(...)

    You also can get the interval associated to each flashcard with get_interval(...).

    Flashcard-box associations are saved as json dictionaries, with the .box extension, in the picker_directory
    (defined in config.py)
    """
    def __init__(self, deck: Deck):
        """
        Initializes the box numbers to 0 for non-registered flashcards.
        """
        self.deck = deck
        # box: Dictionary between flashcard key and box number
        self.box: Dict[str, int] = self.read_interval_boxes(self.deck)
        for card in self.deck:
            if self.get_interval(card) is None:
                self.reset_box(card)

    def get_interval(self, card: FlashCard) -> timedelta:
        """
        @param card: flashcard to get the repetition interval for
        @return: Interval between repetition for the box corresponding to the flashcard
        """
        if card.key not in self.box.keys():
            self.box[card.key] = 0
        return intervals[self.box[card.key]]

    def next_box(self, card: FlashCard) -> None:
        """
        Moves a flashcard to the next box.
        @param card: Flashcard to advance.
        """
        if self.box[card.key] < len(intervals) - 1:
            self.box[card.key] += 1

    def set_box(self, card: FlashCard, num: int) -> None:
        """
        Moves a flashcard to the first box.
        @param card: Flashcard to move.
        @param num: Box number
        """
        self.box[card.key] = min(max(num, 0), len(intervals)-1)

    def reset_box(self, card: FlashCard) -> None:
        """
        Moves a flashcard to the first box.
        @param card: Flashcard to move.
        """
        self.box[card.key] = 0

    def previous_box(self, card: FlashCard):
        """
        Moves a flashcard to the previous box.
        @param card: Flashcard to move.
        """
        if self.box[card.key] > 0:
            self.box[card.key] -= 1

    def get_box(self, card: FlashCard) -> int:
        """
        @param card: Flashcard to get the box for
        @return: The box number of a flashcard
        """
        return self.box[card.key]

    def save(self) -> None:
        """
        Saves the flashcards' boxes to the picker_directory (defined in config.py) with the .box extension.
        """
        with open(os.path.join(picker_directory, self.deck.key + '.box'), 'w') as file:
            json.dump(self.box, file)

    @staticmethod
    def read_interval_boxes(deck: Deck) -> Dict[str, int]:
        """
        @param deck: Deck for which reading the interval boxes
        Reads the flashcards' boxes from the picker_directory (defined in config.py) with the .box extension.
        """
        file_path = os.path.join(picker_directory, deck.key + '.box')
        if not os.path.isfile(file_path):
            return {}
        with open(file_path, 'r') as file:
            return json.load(file)

    def remove_card(self, card: FlashCard):
        if card.key in self.box.keys():
            del self.box[card.key]

    def remove_cards(self, cards: [FlashCard]):
        for card in cards:
            self.remove_card(card)


    def delete(self) -> None:
        """
        Deletes the flashcards' boxes from the picker_directory (defined in config.py) with the .box extension.
        """
        file_path = os.path.join(picker_directory, self.deck.key + '.box')
        if os.path.isfile(file_path):
            os.remove(file_path)

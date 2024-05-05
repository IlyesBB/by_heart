from learn.deck import FlashCard, Deck
from learn.quizz import Historian, TargetTimeTracker, Scheduler, Picker
import time


class Examiner:
    """
    Allows to perform a review of a Deck's flashcards.

    To do a review:
    - Call pick_card() to get a flashcard
    - During this card's review, you can know how much time has passed with get_duration()
    - Call return_card(...) with the review information to end the review and save it

    To know if a review is ongoing, call has_picked_card
    """

    def __init__(self, deck: Deck, historian: Historian, time_tracker: TargetTimeTracker, scheduler: Scheduler) -> None:
        """
        @param deck: Deck to pick flashcards from.
        """
        self.deck: Deck = deck
        self.historian = historian
        self.time_tracker = time_tracker
        self.scheduler = scheduler
        self.picker: Picker = Picker(self.deck, self.historian, self.time_tracker, self.scheduler)
        # start: Time at which the current FlashCard was given. If none, contains 0
        self.start: float = 0

    def pick_card(self) -> FlashCard:
        """
        @return: Picked FlashCard
        """
        card = self.picker.pick_card()
        self.start = time.time()
        return card

    def get_duration(self) -> float:
        """
        @return: Duration in seconds since current card was picked
        """
        return time.time() - self.start

    def return_card(self, card: FlashCard, success: bool) -> None:
        """
        Saves a record for the picked card and reinitializes start time.
        @param card: The flashcard that was being evaluated.
        @param success: True if the response to the flashcard's question was correct.
        """
        self.historian.add_record(card, self.get_duration(), success)
        self.start = 0

    def end(self) -> None:
        """Writes the flashcards' response records, target times, and interval boxes"""
        self.start = 0

    def has_picked_card(self) -> bool:
        """
        @return: True if a flashcard was picked but not returned.
        """
        return self.start != 0

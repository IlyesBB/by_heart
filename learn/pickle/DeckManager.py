import json
import os

from learn.pickle import JSONEncoder, JSONDecoder
from learn.deck import Deck, FlashCard
from learn.quizz import TargetTimeTracker, Scheduler, Historian
from typing import List
from config import decks_directory
from typing import Dict, Set
from copy import copy


class DeckManager:
    """
    Allows to load/save the decks located in the directory decks_directory (config.py).
    Decks are serialized in json format, according to methods defined in JSONEncoder/JSONDecoder classes

    Also manages target times, review schedule and history of reviews of decks.
    Moving between decks or deleting flashcards should be done only with this class methods, and not with Deck class'
    methods.
    """
    time_tracker: Dict[Deck, TargetTimeTracker] = {}
    historian: Dict[Deck, Historian] = {}
    scheduler: Dict[Deck, Scheduler] = {}
    decks: [Deck] = None
    moved_cards: Set[Deck] = set()

    @staticmethod
    def has_moved_cards(deck: Deck):
        if deck not in DeckManager.moved_cards:
            return False
        return True

    @staticmethod
    def get_time_tracker(deck: Deck):
        if deck not in DeckManager.time_tracker.keys():
            DeckManager.time_tracker[deck] = TargetTimeTracker(deck)
        return DeckManager.time_tracker[deck]

    @staticmethod
    def get_historian(deck: Deck):
        if deck not in DeckManager.historian.keys():
            DeckManager.historian[deck] = Historian(deck)
        return DeckManager.historian[deck]

    @staticmethod
    def get_scheduler(deck: Deck):
        if deck not in DeckManager.scheduler.keys():
            DeckManager.scheduler[deck] = Scheduler(deck)
        return DeckManager.scheduler[deck]

    @staticmethod
    def load() -> List[Deck]:
        decks = []
        for deck_file_path in os.listdir(decks_directory):
            with open(os.path.join(decks_directory, deck_file_path), 'r') as deck_file:
                decks.append(json.load(deck_file, cls=JSONDecoder))
        DeckManager.decks = list(decks)
        return decks

    @staticmethod
    def save(deck: Deck) -> None:
        with open(os.path.join(decks_directory, deck.key + '.json'), 'w') as deck_file:
            json.dump(deck, deck_file, cls=JSONEncoder)
        DeckManager.get_historian(deck).save(iterate=(not DeckManager.has_moved_cards(deck)))
        DeckManager.get_scheduler(deck).save()
        DeckManager.get_time_tracker(deck).save()
        DeckManager.moved_cards = set()

    @staticmethod
    def delete(deck: Deck):
        """
        Deletes the deck and all its related files. This operation cannot be undone.
        """
        path = os.path.join(decks_directory, deck.key + '.json')
        if os.path.isfile(path):
            os.remove(path)
        DeckManager.get_historian(deck).delete()
        DeckManager.get_scheduler(deck).delete()
        DeckManager.get_time_tracker(deck).delete()
        DeckManager.remove(deck)

    @staticmethod
    def remove(deck: Deck):
        if deck in DeckManager.time_tracker.keys():
            del DeckManager.time_tracker[deck]
        if deck in DeckManager.historian.keys():
            del DeckManager.historian[deck]
        if deck in DeckManager.scheduler.keys():
            del DeckManager.scheduler[deck]

    @staticmethod
    def move_cards(cards: [FlashCard], origin: Deck, destination: Deck, index_destination=None):
        """
        Moves flashcards between decks. Also moves flashcards' related data (history, target times...)
        @param cards: List of cards to move. If they're not in origin, will throw an error.
        @param origin: Deck containing the cards to move.
        @param destination: Deck to move the cards to.
        @param index_destination: Index at which should be inserted the moved cards.
        """
        # Loading decks' data
        ######################
        target_time_o, target_time_d = DeckManager.get_time_tracker(origin), DeckManager.get_time_tracker(destination)
        scheduler_o, scheduler_d = DeckManager.get_scheduler(origin), DeckManager.get_scheduler(destination)
        historian_o, historian_d = DeckManager.get_historian(origin), DeckManager.get_historian(destination)
        records = historian_o.get_records()
        index_destination = len(destination) if index_destination is None else index_destination
        # Saving cards' data in destination
        ####################################
        historian_d.add_records(records[records['Card'].isin(cards)])
        for ind, card in enumerate(cards):
            target_time_d.set_target_time(card, target_time_o.get_target_time(card))
            scheduler_d.set_box(card, scheduler_o.get_box(card))
            destination.insert_card(index_destination + ind, card)
        # Removing cards' data from origin
        ###################################
        DeckManager.remove_cards(cards, origin)
        DeckManager.moved_cards.add(origin)
        DeckManager.moved_cards.add(destination)

    @staticmethod
    def remove_cards(cards: [FlashCard], origin: Deck):
        """
        Remove cards and their related data (history, target times...) from deck.
        @param cards: List of cards to delete. If they're not in origin, will throw an error.
        @param origin: Deck containing the cards to remove.
        """
        # Loading deck's data
        ######################
        target_time_origin = DeckManager.get_time_tracker(origin)
        scheduler_origin = DeckManager.get_scheduler(origin)
        historian_origin = DeckManager.get_historian(origin)
        # Removing cards' data from deck
        ###################################
        historian_origin.remove_cards(cards)
        target_time_origin.remove_cards(cards)
        scheduler_origin.remove_cards(cards)
        for card in cards:
            origin.remove_card(card)
        DeckManager.moved_cards.add(origin)

    @staticmethod
    def clear(deck: Deck):
        """
        Removes all cards and their related data (history, target times...) from a deck.
        Calls this class' method remove_cards.
        """
        DeckManager.remove_cards(copy(deck.cards), deck)

    @staticmethod
    def remove_card(card: FlashCard, origin: Deck):
        """
        Removes one card and its related data (history, target times...) from a deck.
        Calls this class' method remove_cards.
        """
        DeckManager.remove_cards([card], origin)

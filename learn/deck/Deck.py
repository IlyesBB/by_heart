from learn.deck import FlashCard
from typing import List, Iterator, Callable
from copy import copy
from uuid import uuid4


class Deck:
    """
    A Deck consists a list of FlashCard objects with a title and a unique key.
    """

    def __init__(self, title: str, cards: List[FlashCard] = None) -> None:
        self.cards: List[FlashCard] = [] if cards is None else cards
        self.title = title
        # self.key: Unique ID of the deck
        self.key = str(uuid4())

    def add_card(self, card: FlashCard):
        self.cards.append(card)

    def add_cards(self, cards: [FlashCard]):
        for card in cards:
            self.add_card(card)

    def remove_card(self, card: FlashCard) -> None:
        self.cards.remove(card)

    def remove_cards(self, cards: [FlashCard]) -> None:
        for card in cards:
            self.remove_card(card)

    def insert_card(self, index: int, card: FlashCard):
        self.cards.insert(index, card)

    def insert_cards(self, index: int, cards: [FlashCard]):
        for card_no, card in enumerate(cards):
            self.insert_card(index+card_no, card)

    def __iter__(self) -> Iterator[FlashCard]:
        return iter(self.cards)

    def __getitem__(self, index: int) -> FlashCard:
        return self.cards[index]

    def __delitem__(self, index: int):
        del self.cards[index]

    def __setitem__(self, index: int, card: FlashCard):
        self.cards[index] = card

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        str_list = ["Deck-%s \'%s\'" % (self.key, self.title)]
        for card in self.cards:
            str_list.append(' - ' + str(card))
        return '\n'.join(str_list)

    def __contains__(self, item: FlashCard):
        return item in self.cards

    def __eq__(self, other):
        if not issubclass(other.__class__, Deck):
            return False
        if other.key != self.key:
            return False
        if len(self) != len(other):
            return False
        for card, other_card in zip(self, other):
            if card != other_card:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __copy__(self):
        return Deck(self.title, [copy(card) for card in self.cards])

    def __hash__(self):
        return hash(self.key)

    def filter(self, func: Callable[[FlashCard], bool]):
        cards = list(filter(func, self))
        deck_copy = Deck(self.title, cards)
        deck_copy.key = self.key
        return deck_copy

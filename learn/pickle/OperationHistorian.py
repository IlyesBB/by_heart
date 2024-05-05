from learn.deck import Deck, FlashCard
from learn.pickle import DeckManager


class OperationHistorian:
    operation = []

    @statisMethod
    def add_operation(self, op):
        pass


class Operation:
    def execute(self):
        pass

    def reverse(self):
        pass


class MoveCards(Operation):
    def __init__(self, cards: [FlashCard], origin: Deck, destination: Deck, index_destination=None):
        self.cards = cards
        self.origin = origin
        self.destination = destination
        self.index_destination = index_destination
        self.index_origin = origin.cards.index(cards[0])

    def execute(self):
        DeckManager.move_cards(self.cards, self.origin, self.destination, index_destination=self.index_destination)

    def reverse(self):
        DeckManager.move_cards(self.cards, self.destination, self.origin, index_destination=self.index_origin)


class Cut(Operation):
    def __init__(self, move_cards: MoveCards):
        self.cards = move_cards.cards
        self.origin = move_cards.origin
        self.index_origin = origin.cards.index(cards[0])


class Copy(Operation):
    def __init__(self, move_cards: MoveCards):
        self.cards = move_cards.cards
        self.origin = move_cards.origin


class Paste(Operation):
    def __init__(self, move_cards: MoveCards):
        self.cards = move_cards.cards
        self.destination = move_cards.destination
        self.index_destination = move_cards.index_destination


class AddCards(Operation):
    def __init__(self, cards: [FlashCard], destination: Deck, index_destination=None):
        self.cards = cards
        self.destination = destination
        self.index_destination = index_destination

    def execute(self):
        self.destination.insert_cards(self.index_destination, card)

    def reverse(self):
        self.destination.remove_cards(card)


class AddDeck(Operation):
    def __init__(self, cards: [FlashCard], destination: Deck, index_destination=None):
        self.cards = cards
        self.destination = destination
        self.index_destination = index_destination

    def execute(self):
        self.destination.insert_cards(self.index_destination, card)

    def reverse(self):
        self.destination.remove_cards(card)


class EditFlashCard(Operation):
    def __init__(self, card: FlashCard, question: str, correction: str):
        self.card = card
        self.question, self.correction = question, correction

    def execute(self):
        question_, correction_ = self.card.question, self.card.correction
        self.card.question, self.card.correction = self.question, self.correction
        self.question, self.correction = question_, correction_

    def reverse(self):
        self.execute()


class EditDeckTitle(Operation):
    def __init__(self, deck: Deck, title: str):
        self.deck = deck
        self.title = title

    def execute(self):
        title_ = self.deck.title
        self.deck.title = self.title
        self.title = title_

    def reverse(self):
        self.execute()

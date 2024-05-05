import json
import uuid

from learn.deck import FlashCard, Deck
from learn.pickle import JSONEncoder
from typing import List


class JSONDecoder(json.JSONDecoder):
    """
    Decodes Deck objects in json format.
    """

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(dct):
        if '__class__' not in dct:
            return dct
        if dct['__class__'] == 'FlashCard':
            card = FlashCard(dct['question'], dct['correction'])
            card.key = dct['key']
            return card
        elif dct['__class__'] == 'Deck':
            deck = Deck(dct['title'], dct['cards'])
            deck.key = dct['key']
            return deck
        return dct


if __name__ == '__main__':
    card_ = FlashCard('?', '!', ['tag1', 'tag2'])
    print(card_)
    card_str = json.dumps(card_, cls=JSONEncoder)
    print(json.loads(card_str, cls=JSONDecoder))
    card2 = FlashCard('??', '!!', ['tag2', 'tag3'])
    deck_ = Deck('MyDeck', [card_, card2])
    deck_str = json.dumps(deck_, cls=JSONEncoder)
    print(deck_str)
    print(json.loads(deck_str, cls=JSONDecoder))

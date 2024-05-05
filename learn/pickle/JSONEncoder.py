import json
from learn.deck import FlashCard, Deck


class JSONEncoder(json.JSONEncoder):
    """
    Encodes Deck objects in json format.
    """
    def default(self, obj):
        """
        Serializes objects when used with json. For instance: json.dumps(obj, cls=JSONEncoder)
        Adds a key '__class__' to distinguish dictionaries at decoding.
        @param obj: Can be of type Deck or FlashCard in 'learning.deck' module, or any serializable object
        """
        if isinstance(obj, FlashCard):
            attrs = obj.__dict__.copy()
            attrs['__class__'] = 'FlashCard'
            return attrs
        elif isinstance(obj, Deck):
            attrs = obj.__dict__.copy()
            attrs['__class__'] = 'Deck'
            return attrs
        # Default behavior for all other types
        return super().default(obj)


if __name__ == '__main__':
    card = FlashCard('?', '!', ['Tag1', 'Tag2'])
    print(json.dumps(card, cls=JSONEncoder))

    deck = Deck('My deck')
    print(json.dumps(deck, cls=JSONEncoder))


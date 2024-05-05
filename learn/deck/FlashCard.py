from uuid import uuid4


class FlashCard:
    """
    A FlashCard is a question (front) and a correction (back).
    """

    def __init__(self, question: str, correction: str) -> None:
        self.question = question
        self.correction = correction
        # self.key: Unique id of the card
        self.key = str(uuid4())

    def __repr__(self):
        return 'FlashCard-%s' % self.key

    def __hash__(self):
        return hash(self.key)

    def __copy__(self):
        return FlashCard(self.question, self.correction)

    def __eq__(self, other):
        if not issubclass(other.__class__, FlashCard):
            return False
        if other.key != self.key:
            return False
        if other.question != self.question:
            return False
        if other.correction != self.correction:
            return False
        return True

    def __ne__(self, other):
        return not self == other

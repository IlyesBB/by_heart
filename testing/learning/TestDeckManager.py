import unittest
from learn.deck import FlashCard, Deck
from learn.pickle import DeckManager
from learn.quizz import Scheduler, TargetTimeTracker, Historian
from copy import copy
import pandas as pd
from config import intervals


class TestDeckManager(unittest.TestCase):
    def setUp(self):
        self.deck = Deck("Initial", [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)])
        self.deck_transfer = Deck('Transfer')
        self.deck_transfer.key = 'test2'
        self.deck.key = 'test'
        self.scheduler = Scheduler(self.deck)
        self.time_tracker = TargetTimeTracker(self.deck)
        for ind, card in enumerate(self.deck):
            self.scheduler.next_box(card)
            self.time_tracker.set_target_time(card, ind * 3 / 2)
        self.historian = Historian(self.deck)
        for record_no in range(5):
            for ind, card in enumerate(self.deck):
                self.historian.add_record(card, ind + 1, record_no % 2 == 0)
        DeckManager.save(self.deck)
        self.scheduler.save()
        self.time_tracker.save()
        self.historian.save(iterate=False)

    def testDeleteCards(self):
        cards = list(self.deck.cards[:4])
        DeckManager.remove_cards(cards, self.deck)
        historian = Historian(self.deck)
        scheduler = Scheduler(self.deck)
        time_tracker = TargetTimeTracker(self.deck)
        deck = DeckManager.load()[0]
        for card in cards:
            self.assertNotIn(card, self.deck)
            self.assertNotIn(card, deck)
            self.assertNotIn(card, historian.get_records()['Card'])
            self.assertNotIn(card.key, scheduler.box.keys())
            self.assertNotIn(card.key, time_tracker.target_time.keys())

    def testMoveCards(self):
        deck = self.deck_transfer
        cards = self.deck.cards[:4]
        DeckManager.move_cards(list(cards), self.deck, deck)
        self.historian, historian = Historian(self.deck), Historian(deck)
        self.scheduler, scheduler = Scheduler(self.deck), Scheduler(deck)
        self.time_tracker, time_tracker = TargetTimeTracker(self.deck), TargetTimeTracker(deck)
        for card in cards:
            self.assertNotIn(card, self.deck)
            self.assertNotIn(card, self.historian.get_records()['Card'].tolist())
            self.assertNotIn(card.key, self.scheduler.box.keys())
            self.assertNotIn(card.key, self.time_tracker.target_time.keys())
            self.assertIn(card, deck)
            self.assertIn(card, historian.get_records()['Card'].tolist())
            self.assertIn(card.key, scheduler.box.keys())
            self.assertIn(card.key, time_tracker.target_time.keys())
        for card in self.deck.cards[4:]:
            self.assertIn(card, self.deck)
            self.assertIn(card, self.historian.get_records()['Card'].tolist())
            self.assertIn(card.key, self.scheduler.box.keys())
            self.assertIn(card.key, self.time_tracker.target_time.keys())
            self.assertNotIn(card, deck)
            self.assertNotIn(card, historian.get_records()['Card'].tolist())
            self.assertNotIn(card.key, scheduler.box.keys())
            self.assertNotIn(card.key, time_tracker.target_time.keys())

    def tearDown(self):
        DeckManager.delete(self.deck)
        DeckManager.delete(self.deck_transfer)



if __name__ == '__main__':
    unittest.main()

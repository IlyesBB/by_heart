import random
import pandas as pd
from learn.deck import Deck, FlashCard
from learn.quizz import Historian, TargetTimeTracker, Scheduler
from random import choice
import json
import os
from datetime import datetime
from config import sample_size, warmup_size, factor_max

total_size = sample_size + warmup_size


class Picker:
    """
    Class allowing to choose the next flashcard to review during an exam on a deck.

    Call pick_card method to get the next card. This method assigns a score to each flashcard and return the card with
    the lower score. Call this method each time a new record is added, otherwise it won't work properly.
    """

    def __init__(self, deck: Deck, historian: Historian, time_tracker: TargetTimeTracker, scheduler: Scheduler) -> None:
        self.deck = deck
        self.historian = historian
        self.time_tracker = time_tracker
        self.scheduler = scheduler

    def score(self, card: FlashCard, records: pd.DataFrame = None) -> int:
        """
        Gets the score for a card. Also manages the target response time.

        The possible scores:
        - -1: The card has no target time yet
        - 0: The last response to the card was false, or the target time was exceeded
        - 1: The scheduled time for card review has passed
        - 2: There was at least one error the last time the card was reviewed
        - 3 The response time exceeded the target time at least once the last time the card was reviewed
        - 4: The card doesn't need to be revised

        When a card has no target time, it will be picked at least 5 times in a row. The target response time will be
        the average response time on the last 3 correct responses.
        If multiple responses in a row exceed the target response time (x a factor), it's recalculated.
        It is also reset if the response time was way shorter then the target.

        @param card: Card to get the score for.
        @param records: The deck's records, if already loaded
        @return: The score of the card.
        """
        records = self.historian.get_records() if records is None else records
        # records_card: Records of the selected card
        records_card = records[records['Card'] == card]
        if self.get_target_time(card) is None:
            # The card has no target time yet
            #################################
            if len(records_card) < total_size or not self.last_sample_success(records_card):
                return -1
            else:
                self.init_target_time(records_card)
        elif records.iloc[-1]['Card'] == card:
            # The card was the last reviewed one
            ######################################
            score = self.score_last_card(records_card)
            if score is not None:
                return score
        # The card last review streak reached success and the right response time
        #########################################################################
        if datetime.now() - records_card.iloc[-1]['Date'] > self.scheduler.get_interval(card):
            return 1  # Scheduled review time has passed
        else:
            last_chain = self.get_last_streak(records_card)
            if last_chain['Success'].sum() != len(last_chain):
                return 2  # Failed attempt on last streak
            elif last_chain.apply(self.gt_target_time, axis=1).any():
                return 3  # Exceeded target time on last streak
            return 4

    def score_last_card(self, records_card: pd.DataFrame) -> int | None:
        """
        Calculates the score for a card when it was the last picked card.
        @param records_card: Records filtered for that card.
        @return: The score, if it's 0 or 1. Else, None
        """
        # last: Last record for card
        last = records_card.iloc[-1]
        card = records_card.iloc[-1]['Card']
        if not last['Success']:
            # Failed last attempt
            ##########################
            self.scheduler.reset_box(card)  # If an error was made, the card is set back to first box
            return 0
        elif self.gt_target_time(last):
            # Exceeded target time on last attempt
            #######################################
            # total_streak: True if the last streak length >= total_size
            total_streak = records_card.index[-1] - records_card.index[-total_size] == total_size - 1
            # time_excess: True if exceeded target time at least one during last 'sample_size' streak records
            time_excess = records_card.iloc[-sample_size:].apply(self.gt_target_time, axis=1).all()
            if total_streak and self.last_sample_success(records_card) and time_excess:
                # Target time exceeded several times in a row -> Recalculate target time
                self.init_target_time(records_card)
            else:
                # Target time exceeded for first time of this streak -> Card to previous box
                if records_card.index[-2]+1 != records_card.index[-1]:
                    self.scheduler.previous_box(card)
                return 0
        elif self.lt_target_time(last):
            # Beneath target time on last attempt -> Reset target time
            #########################################################
            self.set_target_time(card, None)
            return -1

    def pick_card(self):
        """
        Attributes a score to each card and picks the one with the lower score.
        See 'score' method for more details on scoring method
        If multiple cards have the same score, will choose one randomly, except for -1 scores.
        For -1 scores, will return the first in alphabetical order of their keys.
        """
        records = self.historian.get_records()
        scores = [(card, self.score(card, records)) for card in self.deck]
        scores.sort(key=lambda x: x[1])
        min_score, ind = scores[0][1], 0
        scores = [(card, score) for (card, score) in scores if score == min_score]
        if min_score != -1:
            card, _ = random.choice(scores)
        else:
            scores.sort(key=lambda x: x[0].key)
            card = scores[0][0]
        return card

    def lt_target_time(self, record_card: pd.Series) -> bool:
        """
        @return: True if record beneath target time.
        @param record_card: Series with fields 'Date', 'Card', 'DurationSeconds' and 'Success'
        """
        target_time = self.get_target_time(record_card['Card'])
        return record_card['DurationSeconds'] < 2 * target_time - target_time * factor_max

    def gt_target_time(self, record_card: pd.Series):
        """
        @return: True if record exceeded target time.
        @param record_card: Series with fields 'Date', 'Card', 'DurationSeconds' and 'Success'
        """
        target_time = self.get_target_time(record_card['Card'])
        return record_card['DurationSeconds'] > target_time * factor_max

    @staticmethod
    def last_sample_success(records_card: pd.DataFrame) -> bool:
        """
        @return: True if last 'sample_size' success values are true
        @param records_card: Dataframe with fields 'Date', 'Card', 'DurationSeconds' and 'Success' for one card
        """
        return records_card.iloc[-sample_size:]['Success'].sum() == sample_size

    @staticmethod
    def get_last_streak(records_card: pd.DataFrame) -> pd.DataFrame:
        """
        @return: Filtered dataframe for last records that were registered in a row.
        @param records_card: Dataframe with fields 'Date', 'Card', 'DurationSeconds' and 'Success' for one card
        """
        ind_last, count = records_card.index[-1], 1
        while count != len(records_card) and records_card.index[-count - 1] == ind_last - count:
            count += 1
        return records_card.iloc[-count:]

    def init_target_time(self, records_card: pd.DataFrame) -> None:
        """
        Recalculates the target time, as the average of the last 'sample_size' records duration
        @param records_card: Dataframe with fields 'Date', 'Card', 'DurationSeconds' and 'Success' for one card
        """
        self.set_target_time(records_card.iloc[-1]['Card'], records_card.iloc[-sample_size:]['DurationSeconds'].mean())

    def set_target_time(self, card: FlashCard, target_time: float | None) -> None:
        """
        Convenience for calling TargetTimeTracker's method with same name
        @param card: Card for which to set the target time
        @param target_time: Duration in seconds or none.
        """
        self.time_tracker.set_target_time(card, target_time)

    def get_target_time(self, card: FlashCard) -> float | None:
        """
        Convenience for calling TargetTimeTracker's method with same name
        @param card: Card for which to get the target time
        @return: Target response time in seconds or none.
        """
        return self.time_tracker.get_target_time(card)


if __name__ == '__main__':
    df = pd.DataFrame({'Success': [True, False, True, False, True, True, True], 'Card': [1]*7})
    print(df['Success'].iloc[-3:].sum())
    df.apply(lambda x: print(x), axis=1)

from learn.deck import FlashCard, Deck
import hashlib
import os
from datetime import datetime as dt
import pandas as pd
from config import records_directory
from typing import List, Tuple, Dict


class Historian:
    """
    Data manager for Examiner class.

    This class gathers the data that will allow to assess performance on flashcards review.

    Allows to:
    - Save flashcard review records
    - Get records in Pandas DataFrame format
    - Write records to a csv file
    - Read records from csv file to Pandas DataFrame

    This class' methods don't take any file path as argument.
    The directories where records are stored are defined in config.py.

    There's one record file per deck.
    Given a deck with key 'deck_key', the record file will be named 'deck_key.csv'
    """

    def __init__(self, deck: Deck) -> None:
        # One record is defined a tuple of 4 variables:
        # - Date: Date of creation of the record, as datetime object.
        # - Card: FlashCard object.
        # - DurationSeconds: Time taken to answer flashcard.
        # - Success: Boolean for the correctness of the answer.
        self.records: List[Tuple[dt, FlashCard, float, bool]] = self.read_records(deck).to_numpy().tolist()
        self.deck: Deck = deck
        self.last_save = dt.now().replace(microsecond=0)

    def add_record(self, card: FlashCard, duration: float, success: bool) -> None:
        """
        Saves a flashcard test. Duration in rounded to the tenth of second, and datetime of test to the second.
        @param card: The flashcard that was being tested
        @param duration: Duration in seconds of the test
        @param success: True if the response to the flashcard was correct, False otherwise
        """
        self.records.append((dt.now().replace(microsecond=0), card, round(duration, 1), success))

    def add_records(self, records: pd.DataFrame):
        self.records.extend(records.to_numpy().tolist())
        self.records.sort(key=lambda x: x[0])

    def get_records(self) -> pd.DataFrame:
        """
        The returned dataframe has 4 fields:
        - Date: Date of creation of the record, as datetime object.
        - Card: FlashCard object.
        - DurationSeconds: Time taken to answer flashcard.
        - Success: Boolean for the correctness of the answer.
        @return: The dataframe of all the flashcards' records for the current deck.
        """
        return pd.DataFrame(self.records, columns=['Date', 'Card', 'DurationSeconds', 'Success'])

    def save(self, iterate=True) -> None:
        """
        Saves flashcards' records to csv file. FlashCard objects are stored as keys. So they can be retrieved (only
        if the corresponding deck is given). datetime objects are stored with format '%d-%m-%Y %H:%M:%S' (like
        '25-03-2024 19:26:48').
        @param iterate: If True, adds records created after this instance creation to file.
        Else, overwrites file with all records
        """
        df = self.get_records()
        df = df.loc[df['Date'] >= self.last_save] if iterate else df
        # Casting object columns to text
        df['Date'] = df['Date'].map(lambda dt_obj: dt.strftime(dt_obj, '%d-%m-%Y %H:%M:%S'))
        # from tabulate import tabulate
        # print(tabulate(df, headers=df.columns))
        df['Card'] = df['Card'].map(lambda card: card.key)
        df = df.rename(columns={'Card': 'CardKey'})

        # Writing records to file
        file_path = os.path.join(records_directory, self.deck.key + '.csv')
        if iterate:
            # noinspection PyTypeChecker
            df.to_csv(file_path, header=(not os.path.isfile(file_path)), index=False, mode='a')
        else:
            # noinspection PyTypeChecker
            df.to_csv(file_path, index=False)

    @staticmethod
    def get_card(key: str, deck: Deck, dict_card: Dict[str, FlashCard] = None) -> FlashCard | None:
        """
        @param key: Unique key of the card
        @param deck: Deck to which the card belong.
        @param dict_card: Dictionary to memoize key-card associations
        """
        if dict_card is not None and key in dict_card.keys():
            return dict_card[key]
        for card in deck:
            if key == card.key:
                if dict_card is not None:
                    dict_card[key] = card
                return card
        raise Exception('Key %s is not in Deck %s' % (key, deck))

    @staticmethod
    def read_records(deck: Deck) -> pd.DataFrame:
        """
        Reads the deck's flashcards' records from csv file.
        One record is defined a tuple of 4 variables:
        - Date: Date of creation of the record, as datetime object.
        - Card: FlashCard object.
        - DurationSeconds: Time taken to answer flashcard.
        - Success: Boolean for the correctness of the answer.
        """
        # noinspection PyTypeChecker
        path: str = os.path.join(records_directory, deck.key + '.csv')
        if not os.path.isfile(path):
            return pd.DataFrame({'Date': [], 'Card': [], 'DurationSeconds': [], 'Success': []})
        df = pd.read_csv(path).rename(columns={'CardKey': 'Card'})
        df['Date'] = df['Date'].map(lambda dt_str: dt.strptime(dt_str, '%d-%m-%Y %H:%M:%S'))
        dict_card = {}

        df['Card'] = df['Card'].map(lambda key: Historian.get_card(key, deck, dict_card))
        return df

    def delete(self):
        """Deletes the deck's records file"""
        # noinspection PyTypeChecker
        path: str = os.path.join(records_directory, self.deck.key + '.csv')
        if os.path.isfile(path):
            os.remove(path)

    def remove_cards(self, cards: [FlashCard]):
        self.records = list(filter(lambda record: record[1] not in cards, self.records))

    def remove_card(self, card: FlashCard):
        self.remove_cards([card])

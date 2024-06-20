import sys
import logging
import random
import argparse
from pathlib import Path


class IteratorException(Exception):
    def __str__(self):
        return "Deck_Iterator requires Deck type or list"


class Flashcard:
    TERM_DICT = dict()
    DEF_DICT = dict()

    def __init__(self, term, definition, ans=0):
        self.term = term
        self.definition = definition
        self.wrong_ans = ans

        Flashcard.TERM_DICT[self.term] = self.definition
        Flashcard.DEF_DICT[self.definition] = self.term

    def guess_me(self, logger=None):
        msg = f'Print the definition of "{self.term}":\n'
        guess = input(msg)

        if guess == self.definition:
            ans = "Correct!"
            print(ans)
        elif guess in Flashcard.DEF_DICT:
            ans = f'Wrong. The right answer is "{self.definition}", but your definition is correct for "{Flashcard.DEF_DICT.get(guess)}".'
            print(ans)
            self.wrong_ans += 1
        else:
            ans = f'Wrong. The right answer is "{self.definition}"'
            print(ans)
            self.wrong_ans += 1

        logger.info(msg)
        logger.info(guess)
        logger.info(ans)

    def __del__(self):
        del Flashcard.TERM_DICT[self.term]
        del Flashcard.DEF_DICT[self.definition]
        del self

    def __eq__(self, other):
        if isinstance(other, Flashcard):
            return self.term == other.term
        elif isinstance(other, str):
            return self.term == other
        return NotImplemented


class Deck:
    def __init__(self, import_path=None, export_path=None):
        self.DECK = []
        self.LOGGER = logging.getLogger(__name__)
        self.LOGGER.setLevel(logging.INFO)
        self._log_path = Path("default_log.log")
        self._file_logger = logging.FileHandler(self._log_path)
        self._log_format = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")
        self._file_logger.setFormatter(self._log_format)
        self.LOGGER.addHandler(self._file_logger)

        self.import_path = import_path
        self.export_path = export_path

        if self.import_path:
            self._internal_import_cards(self.import_path)

    def add(self):
        msg = f"The card:\n"
        term = input(msg)
        self.LOGGER.info(msg)
        self.LOGGER.info(term)
        while term in Flashcard.TERM_DICT:
            msg = f'The term "{term}" already exists. Try again:\n'
            term = input(msg)
            self.LOGGER.info(msg)
            self.LOGGER.info(term)

        msg = f"The definition of the card:\n"
        definition = input(msg)
        self.LOGGER.info(msg)
        self.LOGGER.info(definition)
        while definition in Flashcard.DEF_DICT:
            msg = f'The definition "{definition}" already exists. Try again:\n'
            definition = input(msg)
            self.LOGGER.info(msg)
            self.LOGGER.info(definition)

        card = Flashcard(term, definition)
        self.DECK.append(card)

        ans = f'The pair ("{term}":"{definition}") has been added.'
        print(ans)
        self.LOGGER.info(ans)

    def remove(self):
        msg = "Which card?\n"
        card = input(msg)

        self.LOGGER.info(msg)
        self.LOGGER.info(card)

        if card in self.DECK:
            del self.DECK[self.DECK.index(card)]
            ans = "The card has been removed."
            print(ans)
            self.LOGGER.info(ans)
        else:
            ans = f'Can\'t remove "{card}": there is no such card.'
            print(ans)
            self.LOGGER.info(ans)

    def _internal_import_cards(self, path):
        path = Path(path)
        self.LOGGER.info(path)
        if path.exists():
            with path.open("r") as f:
                num_of_lines = 0
                for line in f.readlines():
                    num_of_lines += 1

                    line = line.strip().split("@@@")

                    term, definition, ans = line

                    if term in self.DECK:
                        del self.DECK[self.DECK.index(term)]
                        self.DECK.append(Flashcard(term, definition, int(ans)))
                        continue
                    self.DECK.append(Flashcard(term, definition))
            ans = f"{num_of_lines} cards have been loaded."
            print(ans)
            self.LOGGER.info(ans)
        else:
            ans = "File not found."
            print(ans)
            self.LOGGER.info(ans)

    def import_cards(self):
        msg = "File name:\n"
        path = input(msg)
        self.LOGGER.info(msg)

        self._internal_import_cards(path)

    def _internal_export_cards(self, path):

        path = Path(path)
        self.LOGGER.info(path)
        iterator = DeckIterator(self.DECK)

        with open(path, "w") as f:
            for card in iterator:
                f.write(f"{card.term}@@@{card.definition}@@@{card.wrong_ans}\n")

        ans = f"{len(self.DECK)} cards have been saved."
        print(ans)
        self.LOGGER.info(ans)

    def export_cards(self):
        msg = "File name:\n"
        path = input(msg)
        self.LOGGER.info(msg)

        self._internal_export_cards(path)

    def ask(self):
        msg = "How many times to ask:\n"
        limit = input(msg)
        self.LOGGER.info(msg)
        self.LOGGER.info(limit)
        try:
            limit = int(limit)
        except ValueError as e:
            print("Are you crazy?")
            self.LOGGER.exception(e)
            sys.exit(e)

        iterator = DeckIterator(self.DECK, infinite_loop=True)
        while limit:
            next(iterator).guess_me(self.LOGGER)
            limit -= 1

    def exit(self):

        if self.export_path:
            self._internal_export_cards(self.export_path)
            self.LOGGER.info("EXIT")
            sys.exit()

        ans = "Bye bye!"
        print(ans)
        self.LOGGER.info(ans)
        sys.exit()

    def log(self):
        path = Path(input("File name:\n"))

        self.LOGGER.info(path)

        self._log_path.rename(path)

        msg = "The log has been saved."
        print(msg)
        self.LOGGER.info(msg)

    def hardest_card(self):
        h_val = max(x.wrong_ans for x in self.DECK) if self.DECK else None

        if h_val:
            h_cards = list(filter(lambda x: x.wrong_ans == h_val, self.DECK))
            if len(h_cards) == 1:
                ans = f'The hardest card is "{h_cards[0].term}". You have {h_val} errors answering it'
                print(ans)
            elif len(h_cards) > 1:
                card_names = f'"{", ".join(x.term for x in h_cards)}"'
                ans = f'The hardest cards are {card_names}. You have {h_val} errors answering it'
                print(ans)
        else:
            ans = "There are no cards with errors."
            print(ans)

        self.LOGGER.info(ans)

    def reset_stats(self):
        for card in self.DECK:
            card.wrong_ans = 0
        ans = "Card statistics have been reset."
        print(ans)

        self.LOGGER.info(ans)


class DeckIterator:
    def __init__(self, deck, infinite_loop=False):
        if isinstance(deck, Deck):
            self.DECK = deck.DECK
        elif isinstance(deck, list):
            self.DECK = deck
        else:
            raise IteratorException
        self._position = 0
        self.infinite_loop = infinite_loop

    def __next__(self):
        try:
            card = self.DECK[self._position]
            self._position += 1
        except IndexError:
            if not self.infinite_loop:
                raise StopIteration

            random.shuffle(self.DECK)
            self._position = 0
            card = self.DECK[self._position]

        return card

    def __iter__(self):
        return self


class TheGame:
    def __init__(self):
        self.DECK = None
        self.ACTIONS = None

    def menu(self):

        parser = argparse.ArgumentParser(description="Improve your memory with flashcards!")

        parser.add_argument("--import_from", help="import path")
        parser.add_argument("--export_to", help="export path")

        args = parser.parse_args()
        kwargs = {"import_path": args.import_from, "export_path": args.export_to}

        self.DECK = Deck(**kwargs)
        self.ACTIONS = {"add": self.DECK.add, "remove": self.DECK.remove, "import": self.DECK.import_cards,
                        "export": self.DECK.export_cards, "ask": self.DECK.ask, "exit": self.DECK.exit,
                        "log": self.DECK.log, "hardest card": self.DECK.hardest_card,
                        "reset stats": self.DECK.reset_stats}

        while True:

            usr_action = input("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):\n")

            self.DECK.LOGGER.info(usr_action)

            usr_action = self.ACTIONS.get(usr_action)

            if not usr_action:
                continue

            usr_action()


if __name__ == "__main__":
    game = TheGame()
    game.menu()

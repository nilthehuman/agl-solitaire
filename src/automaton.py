"""The core class that handles the business logic, i.e. traverses a state machine defined
as a graph in order to generate or check strings for Artificial Grammar Learning experiments."""

import random

import grammar


class Automaton:
    """A finite-state machine that outputs or recognizes valid or invalid strings according
    to a regular grammar."""

    def __init__(self, grammar=None):
        self.grammar = grammar

    def produce_grammatical(self, num_strings=1, min_length=2, max_length=8):
        """Follow the given grammar to output a grammatical string."""
        assert self.grammar is not None
        assert 0 < len(self.grammar.transitions)
        grammatical_strings = set()
        while len(grammatical_strings) < num_strings:
            string = ''
            # keep trying until we get the string length right
            while not min_length <= len(string) <= max_length:
                string = ''
                current_state = 0
                while current_state is not None:
                    # pick a random edge
                    available_symbols = list(self.grammar.transitions[current_state])
                    next_symbol = random.choice(available_symbols)
                    if next_symbol is not None:
                        string += next_symbol
                    # follow the edge to the next state
                    current_state = self.grammar.transitions[current_state][next_symbol]
            grammatical_strings.add(string)
        return grammatical_strings

    def produce_ungrammatical(self):
        #TODO
        pass

    def recognize(self, string):
        """Decide whether the input string conforms to the given grammar."""
        assert self.grammar is not None
        assert 0 < len(self.grammar.transitions)
        state = 0
        while string:
            head = string[0]
            string = string[1:]
            try:
                state = self.grammar.transitions[state][head]
            except KeyError:
                return False
        # can we legally exit from the final state?
        return None in self.grammar.transitions[state]

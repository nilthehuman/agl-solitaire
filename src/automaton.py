"""The core class that handles the business logic, i.e. traverses a state machine defined
as a graph in order to generate or check strings for Artificial Grammar Learning experiments."""

import enum
import random


class Automaton:
    """A finite-state machine that outputs or recognizes valid or invalid strings according
    to a regular grammar."""

    MIN_STRING_LENGTH = 2
    MAX_STRING_LENGTH = 8
    MAX_ATTEMPTS = 10 ** 4

    def __init__(self, grammar=None):
        self.grammar = grammar

    def produce_grammatical(self, num_strings=1, min_length=MIN_STRING_LENGTH, max_length=MAX_STRING_LENGTH, max_attempts=MAX_ATTEMPTS):
        """Follow the given grammar to output grammatical strings."""
        assert self.grammar is not None
        assert 0 < len(self.grammar.transitions)
        grammatical_strings = set()
        # there might not exist num_strings different output strings in the length range
        attempts = 0
        while len(grammatical_strings) < num_strings and attempts < max_attempts:
            string = ''
            # keep trying until we get the string length right
            while not min_length <= len(string) <= max_length and attempts < max_attempts:
                string = ''
                current_state = 0
                while len(string) < max_length and current_state is not None:
                    # pick a random edge
                    available_symbols = list(self.grammar.transitions[current_state])
                    next_symbol = random.choice(available_symbols)
                    if next_symbol is not None:
                        string += next_symbol
                    # follow the edge to the next state
                    current_state = self.grammar.transitions[current_state][next_symbol]
                attempts += 1
            # did we end up in a halting state?
            if current_state is None:
                grammatical_strings.add(string)
        return grammatical_strings

    def produce_ungrammatical(self, num_strings=1, min_length=MIN_STRING_LENGTH, max_length=MAX_STRING_LENGTH):
        """Generate unacceptable strings loosely following Reber & Allen 1978's procedure."""
        class ErrorType(enum.Enum):
            """List of the different kinds of anomalies we can introduce to make a string ungrammatical."""
            WRONG_FIRST = 1
            WRONG_SECOND = 2
            WRONG_PENULTIMATE = 3
            WRONG_TERMINATION = 4
            WRONG_INTERNAL = 5
            BACKWARDS = 6
            RANDOM = 7  # arbitrary UG string made up of the given symbols; not in the original paper
        error_proportions = {
            ErrorType.WRONG_FIRST : 5,
            ErrorType.WRONG_SECOND : 5,
            ErrorType.WRONG_PENULTIMATE : 5,
            ErrorType.WRONG_TERMINATION : 5,
            ErrorType.WRONG_INTERNAL : 2,
            ErrorType.BACKWARDS : 3,
            ErrorType.RANDOM : 5
        }
        ungrammatical_strings = set()
        while len(ungrammatical_strings) < num_strings:
            string = ''
            # pick a random way to create an ungrammatical string
            error_type = random.choices(list(ErrorType), weights=error_proportions.values())[0]
            grammatical_string = self.produce_grammatical(1, min_length=min_length, max_length=max_length).pop()
            if error_type == ErrorType.RANDOM:
                # arbitrary mangled string
                string_length = random.randint(min_length, max_length)
                string = ''.join(random.choice(self.grammar.symbols) for _ in range(string_length))
            elif error_type == ErrorType.BACKWARDS:
                # a grammatical string mirrored i.e. spelled backwards
                string = ''.join(reversed(grammatical_string))
            elif error_type == ErrorType.WRONG_TERMINATION:
                # chop the final symbol off a correct string
                if len(grammatical_string) < min_length + 1:
                    continue  # string not long enough, nevermind
                string = grammatical_string[:-1]
            else:
                # change one letter to break a grammatical string
                wrong_index = None
                if error_type == ErrorType.WRONG_FIRST:
                    wrong_index = 0
                elif error_type == ErrorType.WRONG_SECOND:
                    wrong_index = 1
                elif error_type == ErrorType.WRONG_PENULTIMATE:
                    wrong_index = len(string) - 2
                elif error_type == ErrorType.WRONG_INTERNAL:
                    try:
                        wrong_index = random.randint(2, len(grammatical_string) - 3)
                    except ValueError:
                        continue  # string not long enough, nevermind
                else:
                    assert False
                wrong_symbol = random.choice(self.grammar.symbols)
                while wrong_symbol == grammatical_string[wrong_index]:
                    wrong_symbol = random.choice(self.grammar.symbols)
                string = grammatical_string[:wrong_index] + wrong_symbol + grammatical_string[wrong_index+1:]
            # make sure we didn't get another grammatical string by accident
            if not self.recognize(string) and min_length <= len(string) <= max_length:
                ungrammatical_strings.add(string)
        return ungrammatical_strings

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

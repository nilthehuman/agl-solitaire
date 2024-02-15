"""An implementation of basic regular grammars by way of finite-state automata."""

import abc
import enum
import itertools
import math
import random
import time

random.seed(time.time())


_MIN_STRING_LENGTH = 2
_MAX_STRING_LENGTH = 8
_MAX_ATTEMPTS = 10 ** 4


class Grammar(abc.ABC):
    """The common interface to both kinds of concrete grammar."""

    @abc.abstractmethod
    def obfuscated_repr(self):
        """A marshalled representation of the grammar made unreadable for repeat experiments."""
        raise NotImplementedError

    @abc.abstractmethod
    def randomize(self):
        """Construct an arbitrary grammar."""
        raise NotImplementedError

    @abc.abstractmethod
    def produce_grammatical(self, num_strings, min_length, max_length, max_attempts):
        """Follow the given grammar to output grammatical strings."""
        raise NotImplementedError

    @abc.abstractmethod
    def recognize(self, string):
        """Decide whether the input string conforms to the grammar."""
        raise NotImplementedError

    def produce_ungrammatical(self, num_strings=1, min_length=_MIN_STRING_LENGTH, max_length=_MAX_STRING_LENGTH):
        """Generate unacceptable strings loosely following Reber & Allen 1978's procedure."""
        class ErrorType(enum.Enum):
            """List of the different kinds of deviances we can introduce to make a string ungrammatical."""
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
                string = ''.join(random.choice(self.symbols) for _ in range(string_length))
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
                wrong_symbol = random.choice(self.symbols)
                while wrong_symbol == grammatical_string[wrong_index]:
                    wrong_symbol = random.choice(self.symbols)
                string = grammatical_string[:wrong_index] + wrong_symbol + grammatical_string[wrong_index+1:]
            # make sure we didn't get another grammatical string by accident
            if not self.recognize(string) and min_length <= len(string) <= max_length:
                ungrammatical_strings.add(string)
        return ungrammatical_strings



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class RegularGrammar(Grammar):
    """A regular grammar: a directed graph with an input symbol associated with each edge.
    The whole grammar is represented in a single list of dicts, e.g. the following data
    structure represents the language that starts with one or two A's and then an arbitrary
    number of B's follow. The starting state is number 0. A 'None' index stands for 'OUT'.
    [ {'A': 1}, {'A': 2, 'B': 2, None: None}, {'B': 2, None: None} ]"""

    MIN_STATES = 3
    MAX_STATES = 7
    MIN_PATH_LENGTH = 2

    def __init__(self, symbols=None):
        self.symbols = symbols
        if not symbols:
            self.symbols = ['M', 'R', 'S', 'V', 'X']
        self.transitions = []

    def __repr__(self):
        return str(self.transitions)

    def obfuscated_repr(self):
        """A marshalled representation of the grammar made unreadable for repeat experiments."""
        repr_string = self.__repr__()
        coprimes = (2, 2)
        while 1 != math.gcd(*coprimes):
            coprimes = sorted((random.randrange(95), random.randrange(95)))
        obfuscated_repr_string = ''
        for i, char in enumerate(repr_string):
            # use the ASCII range [32, 126] only
            obfuscated_repr_string += chr(32 + (ord(char) - 32 + coprimes[0] ** i % coprimes[1]) % 95)
        return chr(32 + coprimes[0]) + chr(32 + coprimes[1]) + obfuscated_repr_string

    @classmethod
    def from_repr(cls, repr_string):
        """Restore Grammar from string representation."""
        grammar = cls()
        grammar.transitions = eval(repr_string)
        return grammar

    @classmethod
    def from_obfuscated_repr(cls, obfuscated_repr_string):
        """Restore Grammar from obfuscated string representation."""
        repr_string = ''
        coprimes = (ord(obfuscated_repr_string[0]) - 32,
                    ord(obfuscated_repr_string[1]) - 32)
        obfuscated_repr_string = obfuscated_repr_string[2:]
        repr_string = ''
        for i, char in enumerate(obfuscated_repr_string):
            repr_string += chr(32 + (ord(char) - 32 - coprimes[0] ** i % coprimes[1]) % 95)
        grammar = cls()
        grammar.transitions = eval(repr_string)
        return grammar

    def __str__(self):
        def entry_to_str(i, t):
            if t[0] is None:
                return f"{i} ---> OUT"
            return f"{i} -{t[0]}-> {t[1]}"
        return '\n'.join([entry_to_str(i, t) for i, state in enumerate(self.transitions) for t in state.items()])

    def randomize(self, min_states=None, max_states=None):
        """Construct an arbitrary grammar by choosing states and transitions at random."""
        if min_states is None:
            min_states=RegularGrammar.MIN_STATES
        if max_states is None:
            max_states=RegularGrammar.MAX_STATES
        acceptable = False
        while not acceptable:
            self.transitions = []
            num_states = random.randint(min_states, max_states)
            for _ in range(num_states):
                self.transitions.append({})
                num_transitions = random.randint(0, num_states)
                for _ in range(min(num_transitions, len(self.symbols))):  # avoid inf loop if all symbols are already used up
                    # allow accidentally overwriting a previous entry, that's fine
                    symbol = random.choice(self.symbols + [None])
                    new_state = None
                    if symbol is not None:
                        new_state = random.randrange(num_states)
                        # no more than one edge between the same states
                        while new_state in self.transitions[-1].values():
                            new_state = random.randrange(num_states)
                    self.transitions[-1][symbol] = new_state
            # fix trap states after the fact
            for state in self.transitions:
                if not state:
                    state[None] = None
            # make sure...
            # 1. the graph we got is connected
            # 2. there is at least one exit
            # 3. the exit is reachable (in no fewer than MIN_PATH_LENGTH steps)
            # 4. there is no dead cycle in the graph
            acceptable = (self.is_connected() and
                          any(None in s for s in self.transitions) and
                          RegularGrammar.MIN_PATH_LENGTH <= self.shortest_path_through() < math.inf and
                          not self.has_dead_cycle())

    def is_connected(self):
        """Check if the state graph is made up of a single component."""
        visited = set([0])
        while True:
            visited_new = visited | set(itertools.chain.from_iterable(self.transitions[s].values() for s in visited))
            visited_new -= {None}
            if visited == visited_new:
                break
            visited = visited_new
        return visited == set(range(len(self.transitions)))

    def has_cycle(self):
        """Determine if the graph includes a directed cycle."""
        # make sure we have no trap states (dead ends) left
        assert all(self.transitions)
        # depth-first search
        def dfs(state, path):
            if state is None:
                return False
            if state in path:
                return True
            return any(dfs(edge, path.union(set({state}))) for edge in self.transitions[state].values())
        return dfs(0, set())

    def shortest_path_through(self, starting_state=0):
        """Calculate how many steps it takes to speedrun the graph to an accepting state."""
        # basically a Dijkstra
        def descend(state, visited):
            if None in self.transitions[state]:
                return 0
            visited.add(state)
            reachable_states = set(self.transitions[state].values()) - visited
            if not reachable_states:
                return math.inf
            return 1 + min(map(lambda s: descend(s, visited), reachable_states))
        return descend(starting_state, set())

    def has_dead_cycle(self):
        """Determine if the graph contains a cycle that cannot be escaped."""
        return any(self.shortest_path_through(s) == math.inf for s in range(len(self.transitions)))

    def produce_grammatical(self, num_strings=1, min_length=_MIN_STRING_LENGTH, max_length=_MAX_STRING_LENGTH, max_attempts=_MAX_ATTEMPTS):
        """Follow the given grammar to output grammatical strings."""
        assert 0 < len(self.transitions)
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
                    available_symbols = list(self.transitions[current_state])
                    next_symbol = random.choice(available_symbols)
                    if next_symbol is not None:
                        string += next_symbol
                    # follow the edge to the next state
                    current_state = self.transitions[current_state][next_symbol]
                attempts += 1
            # did we end up in a halting state?
            if current_state is None:
                grammatical_strings.add(string)
        return grammatical_strings

    def recognize(self, string):
        """Decide whether the input string conforms to the given grammar."""
        assert 0 < len(self.transitions)
        state = 0
        while string:
            head = string[0]
            string = string[1:]
            try:
                state = self.transitions[state][head]
            except KeyError:
                return False
        # can we legally exit from the final state?
        return None in self.transitions[state]


# a few example finite state grammars from classic AGL papers

REBER_1967 = RegularGrammar()
REBER_1967.transitions = [ {'T': 1, 'V': 3},
                           {'P': 1, 'T': 2},
                           {'X': 3, 'S': 5},
                           {'X': 3, 'V': 4},
                           {'P': 2, 'S': 5},
                           {None: None}
                         ]

# N.B. this is grammar no. 2 from the paper; grammar 1 is nondeterministic
REBER_ALLEN_1978 = RegularGrammar()
REBER_ALLEN_1978.transitions = [ {'X': 1, 'V': 2},
                                 {'M': 2, 'X': 4},
                                 {'V': 3, 'T': 4},
                                 {'T': 3, 'R': 1},
                                 {'R': 4, 'M': 5, None: None},
                                 {None: None}
                               ]

ABRAMS_REBER_1989 = RegularGrammar()
ABRAMS_REBER_1989 = [ {'X': 0, 'V': 1},
                      {'J': 2, 'X': 3, 'T': 4},
                      {'T': 0, None: None},
                      {'J': 3, None: None},
                      {'V': 3, None: None}
                    ]

KNOWLTON_RAMUS_SQUIRE_1992 = RegularGrammar()
KNOWLTON_RAMUS_SQUIRE_1992.transitions = [ {'L': 0, 'B': 1},
                                           {'F': 2, 'Z': 3, 'L': 4},
                                           {'Z': 0, None: None},
                                           {'F': 3, 'B': 2, None: None},
                                           {None: None}
                                         ]

KNOWLTON_SQUIRE_1994_I = RegularGrammar()
KNOWLTON_SQUIRE_1994_I.transitions = [ {'M': 1, 'V': 4},
                                       {'X': 1, 'V': 2},
                                       {'X': 3, None: None},
                                       {'V': 3, 'R': 1, None: None},
                                       {'R': 4, 'M': 3, None: None}
                                     ]

KNOWLTON_SQUIRE_1994_II = RegularGrammar()
KNOWLTON_SQUIRE_1994_II.transitions = [ {'T': 1, 'F': 3},
                                        {'P': 1, 'T': 2},
                                        {'S': 3, None: None},
                                        {'S': 3, 'F': 4, None: None},
                                        {'P': 2, None: None}
                                      ]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class PatternGrammar(Grammar):
    """A certain kind of non-recursive subregular grammar that consists of a finite set of
    predefined abstract string patterns. The set of all terminal symbols is broken up
    into a number of subsets called classes that may be nested but may not overlap, i.e.
    each pair of classes is either disjoint or one contains the other. Then each pattern
    is defined as a fixed ordered sequence of (possibly repeating) classes, and a string
    generated based on that pattern is a sequence of terminal symbols taken from those
    classes in order. Agreement is currently not implemented in this type of grammar."""

    MIN_CLASSES = 2
    MAX_CLASSES = 6
    MIN_PATTERNS = 2
    MAX_PATTERNS = 5
    MIN_LENGTH = 2
    MAX_LENGTH = 8

    def __init__(self, symbols=None):
        self.symbols = symbols
        if not symbols:
            self.symbols = ['M', 'R', 'S', 'V', 'X']
        self.classes = []
        self.patterns = []

    def obfuscated_repr(self):
        """A marshalled representation of the grammar made unreadable for repeat experiments."""
        # TODO
        return None

    def __repr__(self):
        return str(self)

    def __str__(self):
        def class_to_str(i, c):
            return 'C' + str(i) + ' = ' + str(c)
        def pattern_to_str(i, t):
            return 'T' + str(i) + ' = ' + str(t)
        return '\n'.join([pattern_to_str(i, t) for i, t in enumerate(self.patterns)])
        return '\n'.join([class_to_str(i, c) for i, c in enumerate(self.classes)])
        return '\n'.join([entry_to_str(i, t) for i, state in enumerate(self.transitions) for t in state.items()])

    def randomize(self, min_classes=None, max_classes=None,
                        min_patterns=None, max_patterns=None,
                        min_length=None, max_length=None):
        """Construct an arbitrary pattern grammar."""
        if min_classes is None:
            min_classes=PatternGrammar.MIN_CLASSES
        if max_classes is None:
            max_classes=PatternGrammar.MAX_CLASSES
        if min_patterns is None:
            min_patterns=PatternGrammar.MIN_PATTERNS
        if max_patterns is None:
            max_patterns=PatternGrammar.MAX_PATTERNS
        if min_length is None:
            min_length=PatternGrammar.MIN_LENGTH
        if max_length is None:
            max_length=PatternGrammar.MAX_LENGTH
        self.classes = []
        self.patterns = []
        while not self.classes_okay():
            # partition set of symbols randomly
            self.classes = [set() for _ in range(random.randint(min_classes, max_classes))]
            for symbol in self.symbols:
                # random.choice here?
                self.classes[random.randrange(len(self.classes))].add(symbol)
            for cls in self.classes:
                if not cls:
                    cls.add(random.choice(self.symbols))
        self.patterns = [[] for _ in range(random.randint(min_patterns, max_patterns))]
        for pattern in self.patterns:
            for _ in range(random.randint(min_length, max_length)):
                pattern.append(random.choice(self.classes))

    def classes_okay(self):
        """Verify that current classes aren't trivial, include all symbols and do not overlap."""
        # not all classes singletons?
        if all(len(c) == 1 for c in self.classes):
            return False
        # all symbols covered?
        if set().union(*self.classes) != set(self.symbols):
            return False
        # no overlaps between classes?
        for c1, c2 in itertools.combinations(self.classes, 2):
            if not c1.isdisjoint(c2) and c1.union(c2) - c2 and c2.union(c1) - c1:
                return False
        return True

    # def has_cycle(self):
    #     """Determine if the grammar includes a directed cycle."""
    #     # false by definition: patterns are simple linear tuples
    #     return False

    # def has_dead_cycle(self):
    #     """Determine if the grammar contains a cycle that cannot be escaped."""
    #     # false by definition
    #     raise False

    def produce_grammatical(self, num_strings=1, min_length=_MIN_STRING_LENGTH, max_length=_MAX_STRING_LENGTH, max_attempts=_MAX_ATTEMPTS):
        """Follow the given grammar to output grammatical strings."""
        assert 0 < len(self.classes)
        assert 0 < len(self.patterns)
        grammatical_strings = set()
        suitable_patterns = list(filter(lambda t: min_length <= len(t) <= max_length, self.patterns))
        if not suitable_patterns:
            return set()
        # there might not exist num_strings different output strings in the length range
        attempts = 0
        while len(grammatical_strings) < num_strings and attempts < max_attempts:
            pattern = random.choice(suitable_patterns)
            string = ''.join(map(lambda c: random.choice(list(c)), pattern))
            grammatical_strings.add(string)
        return grammatical_strings

    def recognize(self, string):
        """Decide whether the grammar has a pattern matching the input string."""
        def matches(string, pattern):
            return all(char in cls for char, cls in zip(string, pattern))
        return any(matches(string, pattern) for pattern in self.patterns)

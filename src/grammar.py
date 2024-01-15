"""An implementation of basic regular grammars (equivalent to finite-state automata)."""

import itertools
import math
import random
import time

random.seed(time.time())


class Grammar:
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
        """A marshalled representation of the Grammar made unreadable for repeat experiments."""
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

    def randomize(self, min_states=MIN_STATES, max_states=MAX_STATES):
        """Construct an arbitrary grammar by choosing states and transitions at random."""
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
                          Grammar.MIN_PATH_LENGTH <= self.shortest_path_through() < math.inf and
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

    def shortest_path_through(self, starting_state=0):
        """Calculate how many steps it takes to speedrun the graph to an accepting state."""
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


# a few example finite state grammars from classic AGL papers

REBER_1967 = Grammar()
REBER_1967.transitions = [ {'T': 1, 'V': 3},
                           {'P': 1, 'T': 2},
                           {'X': 3, 'S': 5},
                           {'X': 3, 'V': 4},
                           {'P': 2, 'S': 5},
                           {None: None}
                         ]

# N.B. this is grammar no. 2 from the paper; grammar 1 is nondeterministic
REBER_ALLEN_1978 = Grammar()
REBER_ALLEN_1978.transitions = [ {'X': 1, 'V': 2},
                                 {'M': 2, 'X': 4},
                                 {'V': 3, 'T': 4},
                                 {'T': 3, 'R': 1},
                                 {'R': 4, 'M': 5, None: None},
                                 {None: None}
                               ]

ABRAMS_REBER_1989 = Grammar()
ABRAMS_REBER_1989 = [ {'X': 0, 'V': 1},
                      {'J': 2, 'X': 3, 'T': 4},
                      {'T': 0, None: None},
                      {'J': 3, None: None},
                      {'V': 3, None: None}
                    ]

KNOWLTON_RAMUS_SQUIRE_1992 = Grammar()
KNOWLTON_RAMUS_SQUIRE_1992.transitions = [ {'L': 0, 'B': 1},
                                           {'F': 2, 'Z': 3, 'L': 4},
                                           {'Z': 0, None: None},
                                           {'F': 3, 'B': 2, None: None},
                                           {None: None}
                                         ]

KNOWLTON_SQUIRE_1994_I = Grammar()
KNOWLTON_SQUIRE_1994_I.transitions = [ {'M': 1, 'V': 4},
                                       {'X': 1, 'V': 2},
                                       {'X': 3, None: None},
                                       {'V': 3, 'R': 1, None: None},
                                       {'R': 4, 'M': 3, None: None}
                                     ]

KNOWLTON_SQUIRE_1994_II = Grammar()
KNOWLTON_SQUIRE_1994_II.transitions = [ {'T': 1, 'F': 3},
                                        {'P': 1, 'T': 2},
                                        {'S': 3, None: None},
                                        {'S': 3, 'F': 4, None: None},
                                        {'P': 2, None: None}
                                      ]

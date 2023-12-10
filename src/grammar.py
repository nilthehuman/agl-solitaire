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

    def __init__(self):
        self.symbols = ['M', 'R', 'S', 'V', 'X']
        self.transitions = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '\n'.join([f'{i} -{t[0]}-> {t[1]}' for i, state in enumerate(self.transitions) for t in state.items()])

    def randomize(self):
        """Construct an arbitrary grammar by choosing states and transitions at random."""
        acceptable = False
        while not acceptable:
            self.transitions = []
            num_states = random.randint(Grammar.MIN_STATES, Grammar.MAX_STATES)
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


# TODO: include some standard grammars from classic AGL papers
#reber_allen_1978 = Grammar()
#reber_allen_1978.transitions = []


"""An implementation of basic regular grammars (equivalent to finite-state automata)."""

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
    MIN_LENGTH = 2

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
            # check if you can speedrun the graph in too few steps
            def shortest_path_out(state, visited):
                if None in self.transitions[state]:
                    return 0
                visited.add(state)
                reachable_states = set(self.transitions[state].values()) - visited
                if not reachable_states:
                    return math.inf
                return 1 + min(map(lambda s: shortest_path_out(s, visited), reachable_states))
            # make sure there is at least one exit and it is reachable (in no less than MIN_LENGTH steps)
            acceptable = any(None in s for s in self.transitions) and Grammar.MIN_LENGTH <= shortest_path_out(0, set()) < math.inf


# TODO: include some standard grammars from classic AGL papers
#reber_allen_1978 = Grammar()
#reber_allen_1978.transitions = []


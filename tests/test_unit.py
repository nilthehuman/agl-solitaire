"""Unit tests to check basic expected behaviors."""

import math

from src import automaton, grammar


def test_always_pass():
    assert True


def test_grammar_exit_reachable():
    """See if at least one accepting state is always reachable."""
    g = grammar.Grammar()
    for _ in range(100):
        g.randomize()
        assert g.shortest_path_through() < math.inf


def test_grammar_exit_not_too_close():
    """See if getting to an accepting state takes enough steps."""
    g = grammar.Grammar()
    for _ in range(100):
        g.randomize()
        assert grammar.Grammar.MIN_PATH_LENGTH <= g.shortest_path_through()


def test_automaton_output_long_enough():
    """See if no output strings are below a minimum length."""
    g = grammar.Grammar()
    a = automaton.Automaton(g)
    for _ in range(100):
        g.randomize()
        output_strings = a.produce_grammatical(5)
        print(output_strings)
        assert not any(len(s) < automaton.Automaton.MIN_STRING_LENGTH for s in output_strings)

"""Regression tests: monuments to bugs that once were."""

from src.agl_solitaire import grammar
from src.agl_solitaire import settings
from src.agl_solitaire import utils


def test_grammar_equals_itself():
    """See if a grammar is isomorphic to itself."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        assert g.equal_mod_tokens(g)
    g = grammar.PatternGrammar()
    for _ in range(100):
        g.randomize()
        assert g.equal_mod_tokens(g)


def test_grammar_equals_obfuscated_repr():
    """See if you get the same grammar after a round-trip of obfuscation and deobfuscation."""
    s = settings.Settings()
    s.grammar_class = settings.GrammarClass.REGULAR
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        s.grammar = g.obfuscated_repr()
        g2 = utils.get_grammar_from_obfuscated_repr(s)
        assert g.equal_mod_tokens(g2)
    s.grammar_class = settings.GrammarClass.PATTERN
    g = grammar.PatternGrammar()
    for _ in range(100):
        g.randomize()
        s.grammar = g.obfuscated_repr()
        g2 = utils.get_grammar_from_obfuscated_repr(s)
        assert g.equal_mod_tokens(g2)

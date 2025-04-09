"""Miscellaneous auxiliary functions that don't necessarily belong in any one class."""

from src.agl_solitaire import grammar
from src.agl_solitaire import settings

def get_grammar_from_obfuscated_repr(stngs):
    """Decode and return an object of any Grammar subclass that has an obfuscated representation."""
    try:
        if stngs.grammar_class == settings.GrammarClass.REGULAR:
            gmr = grammar.RegularGrammar.from_obfuscated_repr(stngs.grammar)
        elif stngs.grammar_class == settings.GrammarClass.REGULAR:
            gmr = grammar.PatternGrammar.from_obfuscated_repr(stngs.grammar)
        else:
            # TODO: make custom grammars save/loadable eventually?
            raise NotImplementedError
        gmr.set_tokens(stngs.string_tokens)
        return gmr
    except (IndexError, SyntaxError, TypeError):
        raise ValueError


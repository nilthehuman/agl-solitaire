"""Miscellaneous auxiliary functions that don't necessarily belong in any one class."""

import datetime
import os
import re

from src.agl_solitaire import grammar
from src.agl_solitaire import settings


_LEFT_MARGIN_WIDTH = 2

_builtin_print = print

def print(string='', end='\n'):
    """Smarter print function, adds left margin and wraps long lines automatically."""
    max_width = os.get_terminal_size().columns
    wrapped_string = ''
    string = str(string)
    for line in string.split('\n'):
        carriage_return = re.match(r'\r', line)
        if carriage_return:
            line = line[1:]
        line = ' ' * _LEFT_MARGIN_WIDTH + line
        if carriage_return:
            line = '\r' + line
        while max_width < len(line):
            stop_at = max_width - 1
            # back up to the nearest word boundary
            while 0 <= stop_at and not line[stop_at].isspace():
                stop_at -= 1
            if -1 == stop_at:
                # one giant word, we give up and leave it unwrapped
                stop_at = len(line)
            wrapped_string += line[:stop_at] + '\n'
            line = line[stop_at+1:]
            line = ' ' * _LEFT_MARGIN_WIDTH + line
        wrapped_string += line + '\n'
    # leave off the last newline
    _builtin_print(wrapped_string[:-1], end=end)


_builtin_input = input

def input(prompt='> '):
    """input function with constant left margin for improved readability."""
    return _builtin_input(' ' * _LEFT_MARGIN_WIDTH + prompt)


_which_clear = None

def clear():
    """Find the right clear screen command by trial-and-error and remember it."""
    global which_clear
    try:
        which_clear
    except NameError:
        which_clear = 'cls'
    if os.system(which_clear):
        # non-zero exit code, try the other command
        (which_clear,) = set(['cls', 'clear']) - set([which_clear])
        os.system(which_clear)


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


class Loggable:
    """For classes that want to write most of their output both to screen and to a file."""

    def duplicate_print(self, string, log_only=False):
        """Output the string on the screen and log it in a text file at the same time."""
        if not log_only:
            print(string)
        with open(self.settings.logfile_filename, 'a', encoding='UTF-8') as logfile:
            # prepend timestamp
            stamped_list = ['[' + str(datetime.datetime.now().replace(microsecond=0)) + '] ' + line.strip() for line in string.split('\n')]
            stamped_string = '\n'.join(stamped_list)
            logfile.write(stamped_string + '\n')

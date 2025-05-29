"""Miscellaneous auxiliary functions that don't necessarily belong in any one class."""

import datetime
import os
import re
try:
    import readline
except ModuleNotFoundError:
    # try and fall back on pyreadline3
    try:
        from pyreadline3 import Readline
        readline = Readline()
    except ModuleNotFoundError:
        # nevermind, input history won't be available but that's fine
        pass

from src.agl_solitaire import grammar
from src.agl_solitaire import settings


###  ###  ###  ###  ###  ###  ###  ###
###     TEXT INPUT AND OUTPUT      ###
###  ###  ###  ###  ###  ###  ###  ###

_LEFT_MARGIN_WIDTH = 2

_builtin_print = print

def print(string='', end='\n', left_margin=_LEFT_MARGIN_WIDTH, silent=False):
    """Smarter print function, adds left margin and wraps long lines automatically."""
    string = str(string)
    # add some color to make settings keys and error messages pop too
    try:
        string = re.sub(r"\[(\w)\]", r'[\033[94m\1\033[0m]', string)  # light blue
        string = re.sub(r"warning:", r'\033[33mwarning:\033[0m', string)  # yellow
        string = re.sub(r"error:", r'\033[31merror:\033[0m', string)  # red
    except re.PatternError:
        # pattern not found, that's fine
        pass
    max_width = os.get_terminal_size().columns
    wrapped_string = ''
    for line in string.split('\n'):
        carriage_return = re.match(r'\r', line)
        if carriage_return:
            line = line[1:]
        line = ' ' * left_margin + line
        if carriage_return:
            line = '\r' + line
        while max_width < len(line):
            stop_at = max_width - 1
            # back up to the nearest word boundary
            while 0 <= stop_at and not line[stop_at].isspace():
                stop_at -= 1
            if -1 == stop_at or line[:stop_at].isspace():
                # one giant word, we give up and leave it unwrapped
                stop_at = len(line)
            wrapped_string += line[:stop_at] + '\n'
            line = line[stop_at+1:]
            line = ' ' * left_margin + line
        wrapped_string += line + '\n'
    if not silent:
        _builtin_print(wrapped_string[:-1], end=end)  # leave off the last newline though
    return wrapped_string


_builtin_input = input

def input(prompt='> '):
    """input function with constant left margin for improved readability."""
    return _builtin_input(' ' * _LEFT_MARGIN_WIDTH + prompt)


def clear():
    """Find the right clear screen command by trial-and-error and remember it."""
    global _which_clear
    try:
        _which_clear
    except NameError:
        _which_clear = 'cls'
    if os.system(_which_clear):
        # non-zero exit code, try the other command
        (_which_clear,) = set(['cls', 'clear']) - set([_which_clear])
        os.system(_which_clear)


ansi_term_color_codes = {
    'default'       : 39,
    'red'           : 31,
    'green'         : 32,
    'yellow'        : 33,
    'blue'          : 34,
    'magenta'       : 35,
    'cyan'          : 36,
    'white'         : 37,
    'light red'     : 91,
    'light green'   : 92,
    'light yellow'  : 93,
    'light blue'    : 94,
    'light magenta' : 95,
    'light cyan'    : 96,
    'light white'   : 97,
    #### miscellaneous control codes ####
    'bold'          : 1,
    'center'        : 11111  # fake made-up escape code for centered text
}

ansi_codes_to_names = { val : key for key, val in ansi_term_color_codes.items() }

def pretty_print_color_codes(settings):
    for name, code in ansi_term_color_codes.items():
        if name in ['bold', 'center']:
            continue
        blimp = '*' if name == settings.highlight_color else ' '
        print(f"[{blimp}] \033[{code}m{name}\033[0m")

def colorize(string, settings):
    try:
        code = ansi_term_color_codes[settings.highlight_color]
    except KeyError:
        return string
    if re.search(r" '", string):
        return re.sub(r"(.*) '", r"\033[" + str(code) + r"m\1\033[0m '", string)
    if re.match(r"[^:]*:[^:]*:[^:*]", string):
        # cancel 'last selected option' coloring
        string = re.sub(r"\033\[\d+m", '', string)
        # apply highlight color
        return re.sub(r"(.*:.*):(.*)", r"\1:\033[" + str(code) + r"m\2\033[0m", string)
    return f"\033[{code}m" + string + "\033[0m"

def center(string):
    code = ansi_term_color_codes['center']
    return f"\033[{code}m" + string + "\033[0m"


class Loggable:
    """For classes that want to write most of their output both to screen and to a file."""

    def duplicate_print(self, string, log_only=False):
        """Output the string on the screen and log it in a text file at the same time."""
        if not log_only:
            print(string)
        string_to_log = re.sub(r"\033\[\d+m", '', string)
        with open(self.settings.logfile_filename, 'a', encoding='UTF-8') as logfile:
            # prepend timestamp
            stamped_list = ['[' + str(datetime.datetime.now().replace(microsecond=0)) + '] ' + line.strip() for line in string_to_log.split('\n')]
            stamped_string = '\n'.join(stamped_list)
            logfile.write(stamped_string + '\n')


###  ###  ###  ###  ###  ###  ###  ###
###      STRING MANIPULATION       ###
###  ###  ###  ###  ###  ###  ###  ###

def polish_sentences(sentences):
    """Turn a set of stimuli into their final presentable form."""
    def process(form, meaning):
        # assemble from tuples
        form = ''.join(form)
        meaning = ''.join(meaning)
        # pack superfluous spaces together
        form = re.sub(r"\s+", ' ', form)
        meaning = re.sub(r"\s+", ' ', meaning)
        # get rid of leading/trailing spaces
        form = form.strip()
        meaning = meaning.strip()
        # make them look like actual sentences
        def capitalized(string):
            return string[0].upper() + string[1:]
        form = capitalized(form) + "."
        meaning = "'" + capitalized(meaning) + ".'"
        return form, meaning
    nice_sentences = [process(form, meaning) for form, meaning in sentences]
    # returns a list of pairs
    return nice_sentences

def pad_sentences(sentences):
    """Pad gaps between forms and meanings with spaces and join them."""
    pad_width = 2 + max(len(form) for form, _ in sentences)
    padded_sentences = [form + ' ' * (pad_width - len(form)) + meaning for form, meaning in sentences]
    return padded_sentences


###  ###  ###  ###  ###  ###  ###  ###
###         MISCELLANEOUS          ###
###  ###  ###  ###  ###  ###  ###  ###

def get_grammar_from_obfuscated_repr(stngs):
    """Decode and return an object of any Grammar subclass that has an obfuscated representation."""
    try:
        if stngs.grammar_class == settings.GrammarClass.REGULAR:
            gmr = grammar.RegularGrammar.from_obfuscated_repr(stngs.grammar)
        elif stngs.grammar_class == settings.GrammarClass.PATTERN:
            gmr = grammar.PatternGrammar.from_obfuscated_repr(stngs.grammar)
        else:
            # TODO: make custom grammars save/loadable eventually?
            raise NotImplementedError
        gmr.set_tokens(stngs.string_tokens)
        return gmr
    except (IndexError, SyntaxError, TypeError):
        raise ValueError

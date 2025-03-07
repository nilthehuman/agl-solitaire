"""The application's user interface including the terminal-based menu and the experimental procedure itself."""

import copy
import datetime
import os
import random
import re
import readline
import threading
import time

from src import grammar
from src import settings
from src import version


_LEFT_MARGIN_WIDTH = 2

_builtin_print = print

def print(string='', end='\n'):
    """Smarter print function, adds left margin and wraps long lines automatically."""
    max_width = os.get_terminal_size().columns
    wrapped_string = ''
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

def input(prompt=''):
    """input function with constant left margin for improved readability."""
    return _builtin_input(' ' * _LEFT_MARGIN_WIDTH + prompt)

class Application:
    """The main class responsible for basic user interactions and driving the procedure of the experiment."""

    def __init__(self):
        self.settings = settings.Settings()
        self.settings.load_all_from_ini()

    def duplicate_print(self, string, log_only=False):
        """Output the string on the screen and log it in a text file at the same time."""
        if not log_only:
            print(string)
        with open(self.settings.logfile_filename, 'a', encoding='UTF-8') as logfile:
            # prepend timestamp
            stamped_list = ['[' + str(datetime.datetime.now().replace(microsecond=0)) + '] ' + line.strip() for line in string.split('\n')]
            stamped_string = '\n'.join(stamped_list)
            logfile.write(stamped_string + '\n')

    def main_menu(self):
        """Show the starting menu screen."""
        my_version = version.get_version()
        print('agl-solitaire ' + my_version + '\n-------------------\n\n(a terminal-based tool for double-blind Artificial Grammar Learning experiments)')
        while True:
            print('\n--------  MAIN MENU  --------')
            print('1: [s]tart new experiment session')
            print('2: [r]epeat experiment with previously used grammar')
            print('3: [g]enerate and save grammar for repeat sessions')
            print('4: [c]onfigure settings')
            print('0: [q]uit')
            choice = ''
            while not choice:
                choice = input('> ')
            choice = choice[0].lower()
            if choice in ['1', 's']:
                self.run_experiment()
            elif choice in ['2', 'r']:
                self.load_experiment()
            elif choice in ['3', 'g']:
                self.generate_experiment()
            elif choice in ['4', 'c']:
                self.settings_menu()
            elif choice in ['0', 'q']:
                break
            else:
                print('no such option')

    def generate_grammar(self):
        """Find a grammar that satisfies the protocol's requirements as defined by the user."""
        if self.settings.grammar_class == settings.GrammarClass.REGULAR:
            gmr = grammar.RegularGrammar(self.settings.string_tokens)
        elif self.settings.grammar_class == settings.GrammarClass.PATTERN:
            gmr = grammar.PatternGrammar(self.settings.string_tokens)
        else:
            assert False
        num_required_strings = self.settings.training_strings + self.settings.test_strings_grammatical
        grammatical_strings = []
        max_grammar_attempts = 64
        max_oversize_attempts = 5
        oversize_grammar = 0
        print('Looking for a suitable random grammar...')
        while num_required_strings != len(grammatical_strings) and oversize_grammar <= max_oversize_attempts:
            grammar_attempts = 0
            while num_required_strings != len(grammatical_strings) and grammar_attempts < max_grammar_attempts:
                grammar_attempts += 1
                if self.settings.grammar_class == settings.GrammarClass.REGULAR:
                    gmr.randomize(min_states=gmr.MIN_STATES + oversize_grammar,
                                  max_states=gmr.MAX_STATES + oversize_grammar)
                    gmr.randomize(min_states=gmr.MIN_STATES + oversize_grammar,
                                  max_states=gmr.MAX_STATES + oversize_grammar)
                elif self.settings.grammar_class == settings.GrammarClass.PATTERN:
                    # TODO: oversize pattern grammar
                    gmr.randomize()
                else:
                    assert False
                if not self.settings.recursion and gmr.has_cycle():
                    continue
                grammatical_strings = list(gmr.produce_grammatical(num_strings=num_required_strings,
                                                                   min_length=self.settings.minimum_string_length,
                                                                   max_length=self.settings.maximum_string_length))
            oversize_grammar += 1
            if num_required_strings != len(grammatical_strings):
                print(f"None found, expanding search to between {gmr.MIN_STATES+oversize_grammar} and {gmr.MAX_STATES+oversize_grammar} states...")
        if num_required_strings != len(grammatical_strings):
            print('Sorry, no grammar found that would satisfy the current settings. Try relaxing some of your preferences.')
            return None, None
        print('Grammar selected. The rules of the grammar will be revealed after the session.')
        return gmr, grammatical_strings

    def generate_experiment(self):
        """Generate and serialize a new suitable grammar to file for later use."""
        gmr, _ = self.generate_grammar()
        if not gmr:
            return
        while True:
            filename = input('save to filename (leave empty to cancel): ')
            if not filename:
                return
            go_ahead = True
            if os.path.exists(filename):
                go_ahead = False
                choice = input('warning: file exists, overwrite? (y/n)> ')
                if choice and choice[0].lower() == 'y':
                    go_ahead = True
            if go_ahead:
                self.save_experiment(gmr, filename)
                return

    def save_experiment(self, gmr, filename=None):
        """Serialize current experiment state to file to be run or resumed later."""
        settings_and_gmr = copy.copy(self.settings)
        settings_and_gmr.autosave = False
        settings_and_gmr.grammar = gmr.obfuscated_repr()
        settings_and_gmr.save_all_to_ini(filename)

    def load_experiment(self):
        """Restore a previously generated grammar from a file of the user's choice
        and (re)run the experiment with the same grammar."""
        filename = input('file to load grammar from (leave empty to go back): ')
        if not filename:
            return
        if not os.path.exists(filename):
            print('error: file not found')
            return
        if not os.path.isfile(filename):
            print('error: not a file (maybe a folder?)')
            return
        settings_and_gmr = settings.Settings()
        try:
            settings_and_gmr.load_all(filename)
        except Exception:
            print('error: loading experiment from file failed')
            return
        settings_and_gmr.autosave = False
        if settings_and_gmr.grammar is None:
            print('error: file does not include a grammar')
            return
        try:
            gmr = grammar.RegularGrammar.from_obfuscated_repr(settings_and_gmr.grammar)
        except (IndexError, SyntaxError):
            print('error: loading grammar from file failed')
            return
        settings_without_gmr = copy.copy(settings_and_gmr)
        settings_without_gmr.grammar = None
        if not self.settings.settings_equal(settings_without_gmr):
            print('warning: your current settings differ from those loaded from file:\n')
            print(f"settings in {filename}:\n" + settings_without_gmr.pretty_print())
            print(f"current settings:\n" + self.settings.pretty_print())
            choice = ''
            while not choice:
                choice = input('keep the current settings instead? (y/n)> ')
            if choice[0].lower() != 'y':
                self.settings = settings_and_gmr
        # don't forget to reset tokens as well
        gmr.symbols = self.settings.string_tokens
        self.run_experiment(gmr)

    def settings_menu(self):
        """Enable user to configure and adjust the experimental protocol."""
        while True:
            choice = ''
            print('\n--------  SETTINGS  --------')
            print(f" 1: [u]sername (for the record):\t\t{self.settings.username}")
            print(f" 2: grammar [c]lass:\t\t\t\t{self.settings.grammar_class}")
            print(f" 3: number of training [s]trings:\t\t{self.settings.training_strings}")
            print(f" 4: [t]ime allotted for training:\t\t{self.settings.training_time} seconds")
            print(f" 5: number of [g]rammatical test strings:\t{self.settings.test_strings_grammatical}")
            print(f" 6: number of [u]ngrammatical test strings:\t{self.settings.test_strings_ungrammatical}")
            print(f" 7: mi[n]imum string length:\t\t\t{self.settings.minimum_string_length}")
            print(f" 8: ma[x]imum string length:\t\t\t{self.settings.maximum_string_length}")
            print(f" 9: [l]etters or words to use in strings:\t{self.settings.string_tokens}")
            print(f"10: allow [r]ecursion in the grammar:\t\t{self.settings.recursion}")
            print(f"11: log[f]ile to record sessions in:\t\t{self.settings.logfile_filename}")
            print(f"12: show training strings [o]ne at a time:\t{self.settings.training_one_at_a_time}")
            print(f"13: run pre and post session [q]uestionnaire:\t{self.settings.run_questionnaire}")
            print(' 0: [b]ack to main menu')
            while not choice:
                choice = input('what to change> ')
            if choice.isalpha():
                choice = choice[0].lower()
            attr_to_change = None
            if choice in ['1', 'u']:
                self.settings.username = input('username: ')
                if not self.settings.username:
                    self.settings.username = 'anonymous'
                print(f"good to see you, {self.settings.username}")
            elif choice in ['2', 'c']:
                if self.settings.grammar_class == settings.GrammarClass.REGULAR:
                    self.settings.grammar_class = settings.GrammarClass.PATTERN
                else:
                    self.settings.grammar_class = settings.GrammarClass.REGULAR
            elif choice in ['3', 's']:
                prompt = 'number of training strings: '
                attr_to_change = 'training_strings'
            elif choice in ['4', 't']:
                prompt = 'time allotted for training: '
                attr_to_change = 'training_time'
            elif choice in ['5', 'g']:
                prompt = 'number of grammatical test strings: '
                attr_to_change = 'test_strings_grammatical'
            elif choice in ['6', 'u']:
                prompt = 'number of ungrammatical test strings: '
                attr_to_change = 'test_strings_ungrammatical'
            elif choice in ['7', 'n']:
                prompt = 'minimum string length: '
                attr_to_change = 'minimum_string_length'
            elif choice in ['8', 'x']:
                prompt = 'maximum string length: '
                attr_to_change = 'maximum_string_length'
            elif choice in ['9', 'l']:
                new_tokens = input('tokens to use in strings: ')
                if not new_tokens:
                    print('no tokens provided')
                elif not re.match(r"^[\s\w]+$", new_tokens):
                    print('error: please type letters only')
                elif len(set([*new_tokens])) < 2:
                    print('error: at least two different tokens required')
                else:
                    if re.search(r"\d", new_tokens):
                        print('warning: using numbers in stimuli is not recommended')
                    if re.search(r"[A-Z]", new_tokens) and re.search(r"[a-z]", new_tokens):
                        print('warning: mixing uppercase and lowercase letters is not recommended')
                    if re.search(r"\s", new_tokens):
                        new_tokens = new_tokens.split()
                    self.settings.string_tokens = sorted(list(set([*new_tokens])))
            elif choice in ['10', 'r']:
                self.settings.recursion = not self.settings.recursion
            elif choice in ['11', 'f']:
                new_filename = input('logfile name: ')
                if os.path.exists(new_filename):
                    if not os.path.isfile(new_filename):
                        print('error: not a file (maybe a folder?)')
                    with open(new_filename, 'r', encoding='UTF-8') as logfile:
                        first_few_lines = logfile.readlines()[:10]
                    if not re.search(r'agl-solitaire', '\n'.join(first_few_lines)):
                        print('file does not look like an agl-solitaire log file')
                        while choice not in ['y', 'n']:
                            choice = input('are you sure you want to use this file? (y/n)> ')
                            if choice:
                                choice = choice[0].lower()
                else:
                    while choice not in ['y', 'n']:
                        choice = input('file does not exist, create it? (y/n)> ')
                        if choice:
                            choice = choice[0].lower()
                if choice in ['11', 'f', 'y']:
                    self.settings.logfile_filename = new_filename
            elif choice in ['12', 'o']:
                self.settings.training_one_at_a_time = not self.settings.training_one_at_a_time
            elif choice in ['13', 'q']:
                self.settings.run_questionnaire = not self.settings.run_questionnaire
            elif choice in ['0', 'b']:
                break
            else:
                print('no such setting')
            if attr_to_change is not None:
                new_value = input(prompt)
                try:
                    if int(new_value) != float(new_value):
                        raise ValueError('error: please provide an integer')
                    if int(new_value) < 1:
                        raise ValueError('error: cannot set less than one')
                    if (attr_to_change == 'maximum_string_length' and int(new_value) < self.settings.minimum_string_length or
                        attr_to_change == 'minimum_string_length' and int(new_value) > self.settings.maximum_string_length):
                        raise ValueError('error: minimum string length cannot be larger than maximum string length')
                    # this is not normal, but in Python it is
                    setattr(self.settings, attr_to_change, int(new_value))
                    if (self.settings.training_strings +
                        self.settings.test_strings_grammatical +
                        self.settings.test_strings_ungrammatical) > 100:
                        print('warning: you are advised to keep the total number of training items plus test items under 100')
                except ValueError as err:
                    if err:
                        print(str(err))
                    else:
                        print('error: invalid number')

    def run_experiment(self, gmr=None):
        """Run one session of training and testing with a random grammar and record everything in the log file."""
        # wrap the whole function body in a try block to handle a keyboard interrupt
        def run_experiment_(self, gmr):
            def clear():
                global which_clear
                try:
                    which_clear
                except NameError:
                    which_clear = 'cls'
                if os.system(which_clear):
                    # non-zero exit code, try the other command
                    (which_clear,) = set(['cls', 'clear']) - set([which_clear])
                    os.system(which_clear)
            clear()
            if self.settings.experiment_state and self.settings.experiment_state.test_set:
                if any(judgement is None for (_, _, judgement) in self.settings.experiment_state.test_set):
                    self.duplicate_print('You are now resuming a previously paused session.')
                else:
                    print('You have loaded a previously completed experiment. Do you want to repeat the same experiment? (y/n)')
                    do_repeat = None
                    while do_repeat is None or do_repeat[0] not in ['y', 'n']:
                        do_repeat = input('> ')
                    if 'y' != do_repeat[0]:
                        return
                    self.settings.experiment_state = settings.ExperimentState(False, [], [])
            else:
                self.settings.experiment_state = settings.ExperimentState(False, [], [])
                num_required_grammatical = self.settings.training_strings + self.settings.test_strings_grammatical
                self.duplicate_print('=' * 120, log_only=True)
                grammatical_strings = None
                if gmr is not None:
                    self.duplicate_print('agl-solitaire session started with a pregenerated grammar:')
                    self.duplicate_print(self.settings.pretty_short())
                    self.duplicate_print('Generating training strings and test strings based on the grammar...')
                    grammatical_strings = list(gmr.produce_grammatical(num_strings=num_required_grammatical,
                                                                       min_length=self.settings.minimum_string_length,
                                                                       max_length=self.settings.maximum_string_length))
                else:
                    self.duplicate_print('agl-solitaire session started with the following settings:')
                    self.duplicate_print(self.settings.pretty_print())
                    gmr, grammatical_strings = self.generate_grammar()
                    if gmr is None:
                        return
                    self.duplicate_print('Generating training strings and test strings based on the grammar...')
                # partition grammatical_strings into two subsets
                picked_for_training = random.sample(range(0,num_required_grammatical), k=self.settings.training_strings)
                self.settings.experiment_state.training_set = [grammatical_strings[i] for i in picked_for_training]
                self.settings.experiment_state.test_set = [(grammatical_strings[i], 'y', None) for i in set(range(0,num_required_grammatical)) - set(picked_for_training)]
                self.settings.experiment_state.test_set += [(string, 'n', None) for string in gmr.produce_ungrammatical(num_strings=self.settings.test_strings_ungrammatical,
                                                                                                                        min_length=self.settings.minimum_string_length,
                                                                                                                        max_length=self.settings.maximum_string_length)]
                assert len(self.settings.experiment_state.test_set) == self.settings.test_strings_grammatical + self.settings.test_strings_ungrammatical
                # permute test_set
                random.shuffle(self.settings.experiment_state.test_set)
                self.duplicate_print('Done.')
                if self.settings.run_questionnaire:
                    self.duplicate_print('A few questions before we begin. Feel free to answer as briefly or in as much detail as you like.')
                    self.duplicate_print('Your answers are going to be stored in the log file.')
                    self.duplicate_print('Have you heard about artificial grammar learning experiments before?')
                    answer = input()
                    self.duplicate_print(answer, log_only=True)
                    self.duplicate_print('What languages do you speak?')
                    answer = input()
                    self.duplicate_print(answer, log_only=True)
                    self.duplicate_print('What is your profession if you care to share?')
                    answer = input()
                    self.duplicate_print(answer, log_only=True)
                    self.duplicate_print(f"Out of {len(self.settings.experiment_state.test_set)} questions what do you expect your score to be in this session?")
                    answer = input()
                    self.duplicate_print(answer, log_only=True)
                # end of "else"
            self.duplicate_print(f"You may add any {'further ' if self.settings.run_questionnaire else ''}notes or comments for the record before the training phase begins (optional). Please enter an empty line when you're done:")
            comments = '\n'.join(iter(input, ''))
            self.duplicate_print(comments, log_only=True)
            clear()
            assert self.settings.experiment_state
            if not self.settings.experiment_state.training_finished:
                if self.settings.training_one_at_a_time:
                    time_per_item = round(float(self.settings.training_time) / self.settings.training_strings, 2)
                    self.duplicate_print(f"The training phase will now begin. You will be presented with {self.settings.training_strings} exemplars of the hidden grammar for {time_per_item} seconds each.")
                else:
                    self.duplicate_print(f"The training phase will now begin. You will have {self.settings.training_time} seconds to study a list of {self.settings.training_strings} exemplars of the hidden grammar.")
                self.duplicate_print('Please make sure your screen and terminal font are comfortable to read. Press return when you are ready.')
                self.duplicate_print('You can use a keyboard interrupt (Ctrl-Break on Windows, Ctrl-C on macOS/Unix) to save your progress and exit at any time. You will be able to finish the experiment later.')
                input()
                input_thread = None
                if self.settings.training_one_at_a_time:
                    for string in self.settings.experiment_state.training_set:
                        clear()
                        self.duplicate_print(string)
                        time.sleep(float(self.settings.training_time) / self.settings.training_strings)
                else:
                    self.duplicate_print('Training phase started. Please study the following list of strings:')
                    print()
                    self.duplicate_print('\n'.join(self.settings.experiment_state.training_set))
                    print()
                    input_thread = threading.Thread(target=input, daemon=True)
                    input_thread.start()
                    remaining_time = self.settings.training_time
                    while input_thread.is_alive() and 0 < remaining_time:
                        print(f"\r{remaining_time} seconds remaining (press return to finish early)...  ", end='')
                        time.sleep(1)
                        remaining_time -= 1
                print('\rTraining phase finished.' + ' ' * 30)
                self.duplicate_print('Training phase finished.', log_only=True)
                self.settings.experiment_state.training_finished = True
                clear()
            self.duplicate_print(f"The test phase will now begin. You will be shown {len(self.settings.experiment_state.test_set)} new strings one at a time and prompted to judge the grammaticality of each.")
            self.duplicate_print("You may type 'y' for yes (i.e. grammatical) and 'n' for no (ungrammatical). Press return when you are ready.")
            self.duplicate_print('You can use a keyboard interrupt (Ctrl-Break on Windows, Ctrl-C on macOS/Unix) to save your progress and exit at any time. You will be able to finish the experiment later.')
            # recycle input_thread if it's still running...
            if input_thread and input_thread.is_alive():
                input_thread.join()
            else:
                input()
            # N.B. you can't do the following because you want to update the original test_set
            #for i, item in enumerate(self.settings.experiment_state.test_set):
            for i in range(len(self.settings.experiment_state.test_set)):
                if self.settings.experiment_state.test_set[i][2] is not None:
                    # already answered in a previous session
                    continue
                clear()
                self.duplicate_print(f"Test item #{i+1} out of {len(self.settings.experiment_state.test_set)}. Is the following string grammatical? (y/n)")
                self.duplicate_print(self.settings.experiment_state.test_set[i][0])
                answer = '_'
                while answer[0] not in ['y', 'n']:
                    answer = None
                    while not answer:
                        answer = input('> ')
                    answer = answer[0].lower()
                    if answer == 'g':
                        answer = 'y'
                    elif answer == 'u':
                        answer = 'n'
                self.duplicate_print(answer, log_only=True)
                self.settings.experiment_state.test_set[i] = (self.settings.experiment_state.test_set[i][0], self.settings.experiment_state.test_set[i][1], answer)
            clear()
            self.duplicate_print('Test phase finished. Hope you had fun!')
            if self.settings.run_questionnaire:
                self.duplicate_print('A few more questions if you feel like it:')
                self.duplicate_print('How did you feel during the session?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
                self.duplicate_print('Do you feel like you did well in this session?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
                self.duplicate_print('Did you seem to find any concrete giveaways or hints in the strings?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
            clear()
            self.duplicate_print('And now for the big reveal... Strings were generated using the following regular grammar:')
            self.duplicate_print(str(gmr))
            correct = sum(item[1] == item[2] for item in self.settings.experiment_state.test_set)
            self.duplicate_print(f"You gave {correct} correct answers out of {len(self.settings.experiment_state.test_set)} ({100 * correct/len(self.settings.experiment_state.test_set):.3}%). The answers were the following:")
            # make table columns wider if needed
            width = max(16, 2 + max(len(item[0]) for item in self.settings.experiment_state.test_set))
            self.duplicate_print(f"{'Test string':<{width}}{'Correct answer':<16}{'Your answer':<16}")
            for item in self.settings.experiment_state.test_set:
                self.duplicate_print(f"{item[0]:<{width}}{'yes' if 'y' == item[1] else 'no':<16}{'yes' if 'y' == item[2] else 'no':<16}")
            self.duplicate_print('You now have a chance to add any other post hoc notes or comments for the record if you wish. Please enter an empty line when you\'re done:')
            comments = '\n'.join(iter(input, ''))
            self.duplicate_print(comments, log_only=True)
        try:
            run_experiment_(self, gmr)
        except KeyboardInterrupt:
            self.save_experiment()


if __name__ == '__main__':
    app = Application()
    app.main_menu()

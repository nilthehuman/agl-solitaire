"""The application's user interface including the main menu and the experimental procedure itself."""

import datetime
import os
import random
import re
import readline
import threading
import time

from src import grammar
from src import automaton
from src import settings


_builtin_print = print

def print(string='', end='\n'):
    """Smarter print function, wraps long lines automatically."""
    max_width = os.get_terminal_size().columns
    wrapped_string = ''
    for line in string.split('\n'):
        while max_width < len(line):
            stop_at = max_width - 1
            # back up to the nearest word boundary
            while 0 <= stop_at and not string[stop_at].isspace():
                stop_at -= 1
            if -1 == stop_at:
                # one giant word, we give up and leave it unwrapped
                stop_at = len(line)
            wrapped_string += line[:stop_at] + '\n'
            line = line[stop_at+1:]
        wrapped_string += line + '\n'
    # leave off the last newline
    _builtin_print(wrapped_string[:-1], end=end)


class Application:
    """The main class responsible for basic user interactions."""

    def __init__(self):
        self.settings = settings.Settings()
        self.settings.load_all()

    def duplicate_print(self, string, log_only=False):
        """Output the string on the screen and log it in a text file at the same time."""
        if not log_only:
            print(string)
        with open(self.settings.logfile_filename, 'a', encoding='UTF-8') as logfile:
            # prepend timestamp
            stamped_list = ['[' + str(datetime.datetime.now().replace(microsecond=0)) + '] ' + line for line in string.split('\n')]
            stamped_string = '\n'.join(stamped_list)
            logfile.write(stamped_string + '\n')

    def main_menu(self):
        """Show the starting menu screen."""
        print('agl-solitaire\n-------------\n\n(a terminal-based tool for Artificial Grammar Learning experiments)')
        while True:
            print('\n--- main menu ---')
            print('1: [s]tart experiment session')
            print('2: [c]onfigure settings')
            print('3: [q]uit')
            choice = ''
            while not choice:
                choice = input('> ')
            choice = choice[0].lower()
            if choice in ['1', 's']:
                self.run_experiment()
            elif choice in ['2', 'c']:
                self.settings_menu()
            elif choice in ['3', 'q']:
                break
            else:
                print('no such option')

    def settings_menu(self):
        """Enable user to configure and adjust the experiment's protocol."""
        while True:
            choice = ''
            print('\n--- settings ---')
            print(f"1: number of training [s]trings:\t\t{self.settings.training_strings}")
            print(f"2: [t]ime allotted for training:\t\t{self.settings.training_time} seconds")
            print(f"3: number of [g]rammatical test strings:\t{self.settings.test_strings_grammatical}")
            print(f"4: number of [u]ngrammatical test strings:\t{self.settings.test_strings_ungrammatical}")
            print(f"5: mi[n]imum string length:\t\t\t{self.settings.minimum_string_length}")
            print(f"6: ma[x]imum string length:\t\t\t{self.settings.maximum_string_length}")
            print(f"7: [l]etters to use in strings:\t\t\t{self.settings.string_letters}")
            print(f"8: log[f]ile to record sessions in:\t\t{self.settings.logfile_filename}")
            print('9: [b]ack to main menu')
            while not choice:
                choice = input('what to change> ')
            choice = choice[0].lower()
            attr_to_change = None
            if choice in ['1', 's']:
                prompt = 'number of training strings: '
                attr_to_change = 'training_strings'
            elif choice in ['2', 't']:
                prompt = 'time allotted for training: '
                attr_to_change = 'training_time'
            elif choice in ['3', 'g']:
                prompt = 'number of grammatical test strings: '
                attr_to_change = 'test_strings_grammatical'
            elif choice in ['4', 'u']:
                prompt = 'number of ungrammatical test strings: '
                attr_to_change = 'test_strings_ungrammatical'
            elif choice in ['5', 'n']:
                prompt = 'minimum string length: '
                attr_to_change = 'minimum_string_length'
            elif choice in ['6', 'x']:
                prompt = 'maximum string length: '
                attr_to_change = 'maximum_string_length'
            elif choice in ['7', 'l']:
                new_letters = input('letters to use in strings: ')
                if not new_letters:
                    print('no letters provided')
                elif not re.match(r"^\w+$", new_letters):
                    print('error: please type letters only')
                elif len(set([*new_letters])) < 2:
                    print('error: at least two different letters required')
                else:
                    if re.search(r"\d", new_letters):
                        print('warning: using numbers in stimuli is not recommended')
                    if re.search(r"[A-Z]", new_letters) and re.search(r"[a-z]", new_letters):
                        print('warning: mixing uppercase and lowercase letters is not recommended')
                    self.settings.string_letters = sorted(list(set([*new_letters])))
            elif choice in ['8', 'f']:
                new_filename = input('logfile name: ')
                if os.path.exists(new_filename):
                    if not os.path.isfile(new_filename):
                        print('error: not a file (maybe a folder?)')
                    with open(new_filename, 'r', encoding='UTF-8') as logfile:
                        first_line = logfile.readline()
                    if not re.search(r'agl-solitaire', first_line):
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
                if choice in ['8', 'f', 'y']:
                    self.settings.logfile_filename = new_filename
            elif choice in ['9', 'b']:
                break
            else:
                print('no such setting')
            if attr_to_change is not None:
                new_value = input(prompt)
                try:
                    if int(new_value) != float(new_value):
                        raise ValueError('error: please provide an integer')
                    if int(new_value) < 0:
                        raise ValueError('error: cannot set less than zero')
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
                        print(err)
                    else:
                        print('error: invalid number')

    def run_experiment(self):
        """Run one session of training and testing with a random regular grammar and record everything in the log file."""
        def clear():
            if os.system('cls'):
                # non-zero exit code, try the other command
                os.system('clear')
        clear()
        self.duplicate_print('agl-solitaire session started with the following settings:')
        self.duplicate_print(str(self.settings))
        self.duplicate_print('Looking for a suitable random grammar...')
        gmr = grammar.Grammar(self.settings.string_letters)
        aut = automaton.Automaton(gmr)
        required_strings = self.settings.training_strings + self.settings.test_strings_grammatical
        grammatical_strings = []
        max_attempts = 12
        oversize_grammar = 0
        while required_strings != len(grammatical_strings):
            attempts = 0
            while attempts < max_attempts:
                attempts += 1
                gmr.randomize(min_states=gmr.MIN_STATES + oversize_grammar,
                              max_states=gmr.MAX_STATES + oversize_grammar)
                # TODO: figure out why this call gets stuck :o
                grammatical_strings = list(aut.produce_grammatical(num_strings=required_strings,
                                                                   min_length=self.settings.minimum_string_length,
                                                                   max_length=self.settings.maximum_string_length))
            oversize_grammar += 1
        self.duplicate_print('Grammar selected. The rules of the grammar will be printed at the end of the session.')
        self.duplicate_print('Generating training strings and test strings...')
        # partition grammatical_strings into two subsets
        picked_for_training = random.sample(range(0,required_strings), k=self.settings.training_strings)
        training_set = [grammatical_strings[i] for i in picked_for_training]
        test_set = [(grammatical_strings[i], 'y') for i in set(range(0,required_strings)) - set(picked_for_training)]
        test_set += [(string, 'n') for string in aut.produce_ungrammatical(self.settings.test_strings_ungrammatical)]
        assert len(test_set) == self.settings.test_strings_grammatical + self.settings.test_strings_ungrammatical
        # permute test_set
        random.shuffle(test_set)
        self.duplicate_print('Done.')
        self.duplicate_print('You may add any notes or comments before the training phase begins (optional). Please enter an empty line when you\'re done:')
        comments = '\n'.join(iter(input, ''))
        self.duplicate_print(comments, log_only=True)
        self.duplicate_print(f"The training phase will now begin. You will have {self.settings.training_time} seconds to study a list of {self.settings.training_strings} exemplars.")
        self.duplicate_print('Please press return when you are ready.')
        input()
        self.duplicate_print('Training phase started. Please study the following list of strings:')
        self.duplicate_print('\n'.join(training_set))
        print()
        input_thread = threading.Thread(target=input)
        input_thread.start()
        remaining_time = self.settings.training_time
        while input_thread.is_alive() and 0 < remaining_time:
            print(f"\r{remaining_time} seconds remaining (press return to finish early)...", end='')
            time.sleep(1)
            remaining_time -= 1
        print('\rTraining phase finished.' + ' ' * 20)
        self.duplicate_print('Training phase finished.', log_only=True)
        clear()
        self.duplicate_print(f"The test phase will now begin. You will be shown {len(test_set)} new strings one at a time and prompted to judge the grammaticality of each.")
        self.duplicate_print("You may type 'y' for yes and 'n' for no, or 'g' for grammatical and 'u' for ungrammatical.")
        self.duplicate_print('Please press return when you are ready.')
        input()
        # N.B. you can't do the following because you want to update the original test_set
        #for i, item in enumerate(test_set):
        for i in range(len(test_set)):
            clear()
            print(f"Test item #{i}. Is the following string grammatical? (y/n/g/u)")
            print(test_set[i][0])
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
            test_set[i] = (test_set[i][0], test_set[i][1], answer)
        clear()
        self.duplicate_print('Test phase finished. Hope you had fun!')
        self.duplicate_print('Strings were generated using the following regular grammar:')
        self.duplicate_print(str(gmr))
        correct = sum(item[1] == item[2] for item in test_set)
        self.duplicate_print(f"You gave {correct} correct answers out of {len(test_set)} ({100 * correct/len(test_set)}%). The answers were the following:")
        self.duplicate_print(f"{'Test string':<16}{'Correct answer':<16}{'Your answer':<16}")
        for item in test_set:
            self.duplicate_print(f"{item[0]:<16}{'yes' if 'y' == item[1] else 'no':<16}{'yes' if 'y' == item[2] else 'no':<16}")
        self.duplicate_print('You may now add any post hoc notes or comments if you wish. Please enter an empty line when you\'re done:')
        comments = '\n'.join(iter(input, ''))
        self.duplicate_print(comments, log_only=True)


if __name__ == '__main__':
    app = Application()
    app.main_menu()

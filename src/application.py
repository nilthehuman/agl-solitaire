"""The application's user interface including the main menu and the experimental procedure itself."""

import dataclasses
import datetime
import os
import re
import time

from src import grammar
from src import automaton


@dataclasses.dataclass
class Settings:
    training_strings:           int = 20
    training_time:              int = 300
    test_strings_grammatical:   int = 20
    test_strings_ungrammatical: int = 20
    logfile_filename:           str = 'agl_session.log'


class Application:
    """The main class responsible for basic user interactions."""

    def __init__(self):
        self.settings = Settings

    def duplicate_print(self, string, log_only=False):
        """Output the string on the screen and log it in a text file at the same time."""
        if not log_only:
            print(string)
        with open(self.settings.logfile_filename, 'a', encoding='UTF-8') as logfile:
            logfile.write(string + '\n')

    def main_menu(self):
        """Show the starting menu screen."""
        print('agl-solitaire\n-------------\n\n(a terminal-based tool for Artificial Grammar Learning experiments)')
        while True:
            print('\n--- main menu ---')
            print('1: [s]tart experiment session')
            print('2: [c]hange settings')
            print('3: [q]uit')
            choice = ''
            while not choice:
                choice = input('> ')
            choice = choice[0]
            if choice in ['1', 's']:
                self.run_experiment()
            elif choice in ['2', 'c']:
                self.tweak_settings()
            elif choice in ['3', 'q']:
                break
            else:
                print('no such option')

    def tweak_settings(self):
        """Enable user to adjust game options."""
        while True:
            choice = ''
            print('\n--- settings ---')
            print(f"1: number of training [s]trings:\t\t{self.settings.training_strings}")
            print(f"2: [t]ime allotted for training:\t\t{self.settings.training_time} seconds")
            print(f"3: number of [g]rammatical test strings:\t{self.settings.test_strings_grammatical}")
            print(f"4: number of [u]ngrammatical test strings:\t{self.settings.test_strings_ungrammatical}")
            print(f"5: [l]ogfile to record sessions in:\t\t{self.settings.logfile_filename}")
            print('6: [b]ack to main menu')
            while not choice:
                choice = input('what to change> ')
            choice = choice[0]
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
            elif choice in ['5', 'l']:
                new_filename = input('logfile name: ')
                if os.path.exists(new_filename):
                    if not os.path.isfile(new_filename):
                        print('error: not a file (maybe a folder?)')
                    with open(new_filename, 'r', encoding='UTF-8') as logfile:
                        first_line = logfile.readline()
                    if not re.match(r'^agl-solitaire', first_line):
                        print('file does not look like an agl-solitaire log file')
                        while choice not in ['y', 'n']:
                            choice = input('are you sure you want to use this file? (y/n)> ')
                            if choice:
                                choice = choice[0]
                else:
                    while choice not in ['y', 'n']:
                        choice = input('file does not exist, create it? (y/n)> ')
                        if choice:
                            choice = choice[0]
                if choice in ['5', 'l', 'y']:
                    self.settings.logfile_filename = new_filename
            elif choice in ['6', 'b']:
                break
            else:
                print('no such setting')
            if attr_to_change is not None:
                new_value = input(prompt)
                try:
                    if int(new_value) < 0:
                        raise ValueError
                    # this is not normal, but in Python it is
                    setattr(self.settings, attr_to_change, int(new_value))
                except ValueError:
                    print('error: invalid number')

    def run_experiment(self):
        """Run one session of training and testing with a random regular grammar and record everything in the log file."""
        gmr = grammar.Grammar()
        gmr.randomize()
        aut = automaton.Automaton(gmr)
        if os.system('cls'):
            # non-zero exit code, try the other command
            os.system('clear')
        self.duplicate_print(f"agl-solitaire session started at {datetime.datetime.now().replace(microsecond=0)} with the following settings:")
        for field in dataclasses.fields(self.settings):
            self.duplicate_print(f"{field.name}: {getattr(self.settings, field.name)}")
        self.duplicate_print('You may now add any notes or comments before the training phase begins (optional). Please enter an empty line when you\'re done:')
        comments = '\n'.join(iter(input, ''))
        self.duplicate_print(comments, log_only=True)
        self.duplicate_print(f"The training phase will now begin. You will have {self.settings.training_time} seconds to study the exemplars. Please press return when you are ready.")
        input()
        self.duplicate_print(f"Training phase started at {datetime.datetime.now().replace(microsecond=0)}. Please study the following list of strings:")
        self.duplicate_print('\n'.join(aut.produce_grammatical(self.settings.training_strings)))
        print()
        remaining_time = self.settings.training_time
        while 0 < remaining_time:
            print(f"\r{remaining_time} seconds remaining...  ", end='')
            time.sleep(1)
            remaining_time -= 1
        print(f"\rTraining phase finished.      ")
        self.duplicate_print(f"Training phase finished.", log_only=True)
        self.duplicate_print(f"Testing phase started at {datetime.datetime.now().replace(microsecond=0)}.")
        # TODO measure subject's performance and show results
        self.duplicate_print('You may now add any post hoc notes or comments (optional). Please enter an empty line when you\'re done:')
        comments = '\n'.join(iter(input, ''))
        self.duplicate_print(comments, log_only=True)


if __name__ == '__main__':
    app = Application()
    app.main_menu()

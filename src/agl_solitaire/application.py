"""The application's user interface including the terminal-based menu and the experimental procedure itself."""

import copy
import os
os.system("")  # apparently makes Windows terminal handle ANSI escape sequences too
import re
import smtplib
import sys

from src.agl_solitaire import custom_helpers
from src.agl_solitaire import experiment
from src.agl_solitaire import grammar
from src.agl_solitaire import settings
from src.agl_solitaire import task_state
from src.agl_solitaire import version
from src.agl_solitaire.utils import print, input, clear, get_grammar_from_obfuscated_repr, Loggable


class Application(Loggable):
    """The main class responsible for basic user interactions and initiating experiments."""

    def __init__(self):
        self.settings = settings.Settings()
        self.settings.load_all()
        # load custom experiment scripts from the custom/ directory
        self.custom_experiments = custom_helpers.load_custom_experiments()

    def main_menu(self):
        """Show the starting menu screen."""
        my_version = version.get_version()
        print('agl-solitaire ' + my_version + '\n-------------------\n\n(a terminal-based tool for double-blind Artificial Grammar Learning experiments)')
        while True:
            print('\n--------  MAIN MENU  --------')
            print('1: [s]tart new experiment session')
            print('2: [l]oad/resume experiment')
            print('3: [g]enerate and save experiment for later sessions')
            print('4: [c]onfigure settings')
            print('0: [q]uit')
            choice = ''
            while not choice:
                choice = input()
            choice = choice[0].lower()
            if choice in ['1', 's']:
                self.start_new_experiment()
            elif choice in ['2', 'l']:
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
        """Find a grammar that satisfies the experimental protocol's requirements as defined by the user."""
        if self.settings.grammar_class == settings.GrammarClass.REGULAR:
            gmr = grammar.RegularGrammar(self.settings.string_tokens)
        elif self.settings.grammar_class == settings.GrammarClass.PATTERN:
            gmr = grammar.PatternGrammar(self.settings.string_tokens)
        else:
            raise NotImplementedError
        num_required_strings = self.settings.training_strings + self.settings.test_strings_grammatical
        grammatical_strings = None
        ungrammatical_strings = None
        max_grammar_attempts = 64
        max_oversize_attempts = 5
        oversize = 0
        self.duplicate_print('Looking for a suitable random grammar...')
        # TODO: move this whole loop to the Grammar classes
        while (grammatical_strings is None or ungrammatical_strings is None) and oversize <= max_oversize_attempts:
            grammar_attempts = 0
            while (grammatical_strings is None or ungrammatical_strings is None) and grammar_attempts < max_grammar_attempts:
                grammar_attempts += 1
                if self.settings.grammar_class == settings.GrammarClass.REGULAR:
                    gmr.randomize(min_states=gmr.MIN_STATES + oversize,
                                  max_states=gmr.MAX_STATES + oversize)
                elif self.settings.grammar_class == settings.GrammarClass.PATTERN:
                    gmr.randomize(min_classes=gmr.MIN_CLASSES + int(oversize/2 + 0.5),
                                  max_classes=gmr.MAX_CLASSES + int(oversize/2 + 0.5),
                                  min_patterns=gmr.MIN_PATTERNS + int(oversize/2),
                                  max_patterns=gmr.MAX_PATTERNS + int(oversize/2),
                                  min_length=self.settings.minimum_string_length,
                                  max_length=self.settings.maximum_string_length)
                else:
                    assert False
                if not self.settings.recursion and gmr.has_cycle():
                    continue
                grammatical_strings = gmr.produce_grammatical(num_strings=num_required_strings,
                                                              min_length=self.settings.minimum_string_length,
                                                              max_length=self.settings.maximum_string_length)
                ungrammatical_strings = gmr.produce_ungrammatical(num_strings=self.settings.test_strings_ungrammatical)
            oversize += 1
            if (grammatical_strings is None or ungrammatical_strings is None) and oversize <= max_oversize_attempts:
                if self.settings.grammar_class == settings.GrammarClass.REGULAR:
                    self.duplicate_print(f"None found, expanding search to {gmr.MIN_STATES+oversize} to {gmr.MAX_STATES+oversize} states...")
                elif self.settings.grammar_class == settings.GrammarClass.PATTERN:
                    class_oversize = int(oversize/2 + 0.5)
                    pattern_oversize = int(oversize/2)
                    self.duplicate_print(f"None found, expanding search to {gmr.MIN_CLASSES+class_oversize} to {gmr.MAX_CLASSES+class_oversize} word classes and {gmr.MIN_PATTERNS+pattern_oversize} to {gmr.MAX_PATTERNS+pattern_oversize} patterns...")
                else:
                    assert False
        if (grammatical_strings is None or ungrammatical_strings is None):
            self.duplicate_print('Sorry, no grammar found that would satisfy the current settings. Try relaxing some of your preferences.')
            return None, None, None
        # TODO: this should especially be moved to the Grammars
        gmr.tokens = None
        self.duplicate_print('Grammar selected. The rules of the grammar will be revealed after the session.')
        return gmr, list(grammatical_strings), list(ungrammatical_strings)

    def generate_experiment(self):
        """Generate and serialize a new suitable grammar to file for later use."""
        try:
            gmr, _, _ = self.generate_grammar()
        except NotImplementedError:
            print('error: saving custom grammars to file is not supported (yet)')
            return
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
                settings_and_gmr = copy.copy(self.settings)
                settings_and_gmr.autosave = False
                settings_and_gmr.grammar = gmr.obfuscated_repr()
                # FIXME: probably save to remove for good, right?
                # settings_and_gmr.halted_task = task.Task()
                settings_and_gmr.save_all(filename)
                return

    def load_experiment(self):
        """Resume a previously generated experiment from a file of the user's choice
        and (re)run the experiment with the same grammar."""
        filename = input('file to load grammar from (leave blank to use default settings file): ')
        if not filename:
            filename = None
        else:
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
        if settings_and_gmr.halted_task is None or not settings_and_gmr.halted_task.ready():
            if settings_and_gmr.grammar is None:
                print('error: file does not include a grammar or a paused experiment')
                return
            try:
                get_grammar_from_obfuscated_repr(settings_and_gmr)
            except ValueError:
                print('error: loading grammar from file failed')
                return
            settings_and_gmr.halted_task = task_state.TaskState(settings_and_gmr)
        print(f"Experiment loaded from '{settings_and_gmr.filename}'.")
        if not self.settings.settings_equal(settings_and_gmr):
            print('warning: your current settings differ from those loaded from file:\n')
            print(f"settings in '{filename}':\n" + settings_and_gmr.diff(self.settings))
            print(f"current settings:\n" + self.settings.diff(settings_and_gmr))
            choice = ''
            while not choice:
                choice = input('use the current settings instead? (y/n)> ')
            if choice[0].lower() == 'y':
                settings_and_gmr.override(self.settings)
        # TODO: rephrase this condition in terms of Task.ready?
        if all(judgement is None for (_, _, judgement) in settings_and_gmr.halted_task.test_set):
            self.duplicate_print('=' * 120, log_only=True)
            self.duplicate_print('You are now starting a previously generated experiment:')
            self.duplicate_print(settings_and_gmr.pretty_short())
        elif any(judgement is None for (_, _, judgement) in settings_and_gmr.halted_task.test_set):
            self.duplicate_print('You are now resuming a previously paused session.')
        else:
            print('You have loaded a previously completed experiment. Do you want to repeat the same experiment all over again? (y/n)')
            do_repeat = None
            while not do_repeat or do_repeat[0].lower() not in ['y', 'n']:
                do_repeat = input()
            if 'y' != do_repeat[0].lower():
                return
            # FIXME: this is probably safe to remove right?
            def callback():
                settings_and_gmr.halted_task = task_state.TaskState(settings_and_gmr)
            settings_and_gmr.without_autosave(callback)
        self.run_experiment(settings_and_gmr)

    def settings_menu(self):
        """Enable user to configure and adjust the experimental protocol."""
        while True:
            print('\n--------  SETTINGS  --------')
            # used for disabling currently unavailable options
            settings_enabled = settings.SettingsEnabled()
            # used for not showing currently unavailable options
            settings_display = copy.copy(self.settings)
            settings_display.autosave = False
            # recursion is only available in regular grammars
            if self.settings.grammar_class != settings.GrammarClass.REGULAR:
                settings_enabled.recursion = False
                settings_display.recursion = '--'
            # repetitions is only available when showing strings one at a time
            if not self.settings.training_one_at_a_time:
                settings_enabled.training_reps = False
                settings_display.training_reps = '--'
            # custom experiments may disregard settings arbitrarily
            if self.settings.grammar_class.custom():
                mod = sys.modules[custom_helpers.CUSTOM_MODULE_PREFIX + self.settings.grammar_class.name]
                settings_used = mod.CustomExperiment.settings_used
                settings_enabled.mask_unused(settings_used)
                settings_display.mask_unused(settings_used, mask_value='--')
            options = [
                f" 1: [u]sername (for the record):\t\t{settings_display.username}",
                f" 2: grammar [c]lass:\t\t\t\t{settings_display.grammar_class}{' (custom)' if self.settings.grammar_class.custom() else ''}",
                f" 3: number of training [s]trings:\t\t{settings_display.training_strings}",
                f" 4: [t]ime allotted for training:\t\t{settings_display.training_time} seconds",
                f" 5: number of [g]rammatical test strings:\t{settings_display.test_strings_grammatical}",
                f" 6: number of [u]ngrammatical test strings:\t{settings_display.test_strings_ungrammatical}",
                f" 7: mi[n]imum string length:\t\t\t{settings_display.minimum_string_length}",
                f" 8: ma[x]imum string length:\t\t\t{settings_display.maximum_string_length}",
                f" 9: [l]etters or words to use in strings:\t{settings_display.string_tokens}",
                f"10: allow recursion in the grammar:\t\t{settings_display.recursion}",
                f"11: log[f]ile to record sessions in:\t\t{settings_display.logfile_filename}",
                f"12: show training strings [o]ne at a time:\t{settings_display.training_one_at_a_time}",
                f"13: number of training [r]epetitions:\t\t{settings_display.training_reps}{' round(s)' if settings_enabled.training_reps else ''}",
                f"14: run pre and post session [q]uestionnaire:\t{settings_display.run_questionnaire}",
                f"15: automatically [e]mail logs to author:\t{settings_display.email_logs}",
                ' 0: [b]ack to main menu'
            ]
            for i, option in enumerate(options):
                option_num = re.match(r"\s*(\d+)", option).group(1)
                option_letter = None
                if letter_search := re.search(r"\[(\w)\]", option):
                    option_letter = letter_search.group(1)
                try:
                    if choice in [option_num, option_letter]:
                        # highlight last selected value
                        colon_match = re.match(r"(.*:.*):(.*)", option)
                        options[i] = colon_match.group(1) + ":\033[31m" + colon_match.group(2) + "\033[0m"
                except UnboundLocalError:
                    # choice variable has not been assigned
                    pass
            print("\n".join(options))
            choice = ''
            while not choice:
                choice = input('what to change> ')
            if choice.isalpha():
                choice = choice[0].lower()
            choice_to_attr_name = {
                '1'  : 'username',
                'u'  : 'username',
                '2'  : 'grammar_class',
                'c'  : 'grammar_class',
                '3'  : 'training_strings',
                's'  : 'training_strings',
                '4'  : 'training_time',
                't'  : 'training_time',
                '5'  : 'test_strings_grammatical',
                'g'  : 'test_strings_grammatical',
                '6'  : 'test_strings_ungrammatical',
                'u'  : 'test_strings_ungrammatical',
                '7'  : 'minimum_string_length',
                'n'  : 'minimum_string_length',
                '8'  : 'maximum_string_length',
                'x'  : 'maximum_string_length',
                '9'  : 'string_tokens',
                'l'  : 'string_tokens',
                '10' : 'recursion',
                '11' : 'logfile_filename',
                'f'  : 'logfile_filename',
                '12' : 'training_one_at_a_time',
                'o'  : 'training_one_at_a_time',
                '13' : 'training_reps',
                'r'  : 'training_reps',
                '14' : 'run_questionnaire',
                'q'  : 'run_questionnaire',
                '15' : 'email_logs',
                'e'  : 'email_logs'
            }
            try:
                if not getattr(settings_enabled, choice_to_attr_name[choice]):
                    print('error: that option is not available for this kind of experiment')
                    choice = ''
                    continue
            except KeyError:
                # fall through and let the logic below handle it
                pass
            attr_to_change = None
            if choice in ['1', 'u']:
                self.settings.username = input('username: ')
                if not self.settings.username:
                    self.settings.username = 'anonymous'
                print(f"good to see you, {self.settings.username}")
            elif choice in ['2', 'c']:
                self.settings.grammar_class = self.settings.grammar_class.next()
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
            elif choice in ['10']:
                self.settings.recursion = not self.settings.recursion
            elif choice in ['11', 'f']:
                new_filename = input('logfile name: ')
                print('\'' + new_filename + '\'')
                if not new_filename:
                    continue  # nevermind
                elif os.path.exists(new_filename):
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
            elif choice in ['13', 'r']:
                prompt = 'number of rounds to repeat training data: '
                attr_to_change = 'training_reps'
            elif choice in ['14', 'q']:
                self.settings.run_questionnaire = not self.settings.run_questionnaire
            elif choice in ['15', 'e']:
                self.settings.email_logs = not self.settings.email_logs
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

    def start_new_experiment(self):
        """Create a brand new random grammar based on user's settings, run the experimental procedure and record everything in the log file."""
        clear()
        self.duplicate_print('=' * 120, log_only=True)
        self.duplicate_print('agl-solitaire session started with the following settings:')
        self.duplicate_print(self.settings.pretty_print())
        if not self.settings.grammar_class.custom():
            gmr, _grammatical_strings, _ungrammatical_strings = self.generate_grammar()
            if gmr is None:
                return
            self.settings.grammar = gmr.obfuscated_repr()
        self.settings.halted_task = None
        self.run_experiment()

    def run_experiment(self, stngs=None):
        """Run one session of training and testing with a random grammar and record everything in the log file."""
        # wrap the whole function body in a try block to handle a keyboard interrupt
        try:
            if stngs is None:
                stngs = self.settings
            assert stngs.halted_task is not None or stngs.grammar is not None
            if not stngs.grammar_class.custom():
                experiment_to_run = experiment.Experiment(stngs)
            else:
                custom_module = sys.modules[custom_helpers.CUSTOM_MODULE_PREFIX + self.settings.grammar_class.name]
                experiment_to_run = custom_module.CustomExperiment(stngs)
            if not experiment_to_run.ready():
                self.duplicate_print('Generating training strings and test strings for the experiment...')
                ### generate training and test material ###
                prepare_successful = experiment_to_run.prepare()
                ### ### ### ### ### ### ### ### ### ### ###
                if not prepare_successful:
                    self.duplicate_print('Sorry, it looks like the selected grammar cannot produce the required number of different training and test strings.')
                    if stngs.test_strings_grammatical:
                        self.duplicate_print('Try lowering the number of strings to use and try again.')
                    self.duplicate_print('Setup failed. Aborting experiment.')
                    return
                self.duplicate_print('Done.')
            assert experiment_to_run.ready()
            if stngs.run_questionnaire:
                self.duplicate_print('A few questions before we begin. Feel free to answer as briefly or in as much detail as you like.')
                self.duplicate_print('Your answers are going to be recorded in the log file.')
                self.duplicate_print('Have you heard about artificial grammar learning experiments before?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
                self.duplicate_print('What languages do you speak?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
                self.duplicate_print('What is your profession if you care to share?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
            self.duplicate_print(f"You may add any {'further ' if stngs.run_questionnaire else ''}notes or comments for the record before the training phase begins (optional). Please enter an empty line when you're done:")
            comments = '\n'.join(iter(input, ''))
            self.duplicate_print(comments, log_only=True)
            clear()
            ### now perform the main part of the experiment ###
            experiment_to_run.run()
            ### ### ### ### ### ### ### ### ### ### ### ### ###
            if stngs.email_logs:
                go_ahead = True
                while go_ahead:
                    go_ahead = False
                    print('Sending experiment logs to the author of the application...')
                    with open(stngs.logfile_filename, 'r') as fh:
                        log_lines = fh.read().split('\n')
                    try:
                        from_line = len(log_lines) - 1 - next(i for i, line in enumerate(log_lines[::-1]) if '====' in line)
                    except StopIteration:
                        # oh well, let's just send the whole file
                        from_line = 0
                    message_body = 'Subject: experiment logs\n\n' + '\n'.join(log_lines[from_line:])
                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                            # all in plaintext, probably not a good idea :(
                            server.login('aglsolitaire@gmail.com', 'llot gfpy csfw wuyt')
                            server.sendmail('aglsolitaire@gmail.com', 'aglsolitaire@gmail.com', message_body)
                        print('Success. Thank you for your contribution!')
                    except OSError:
                        print('Failed. Perhaps your internet connection is not working.')
                        print('Do you want to try again? (y/n)')
                        answer = input()
                        if answer and answer[0].lower() == 'y':
                            go_ahead = True
                    except Exception:
                        print('Failed, reason unknown. Sorry. :(')
        except KeyboardInterrupt:
            print()
            self.duplicate_print(f"Experiment halted by user. Progress saved to '{stngs.filename}'.")
            # returning to main menu
        finally:
            try:
                experiment_to_run.cleanup()
            except UnboundLocalError:
                pass


if __name__ == '__main__':
    app = Application()
    app.main_menu()

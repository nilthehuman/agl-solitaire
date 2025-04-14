"""Class responsible for driving most of the actual experimental procedure."""

import dataclasses
import random
import threading
import time
import typing

try:
    random.seeded
except AttributeError:
    random.seed(time.time())
    random.seeded = True


from src.agl_solitaire.grammar import Grammar
from src.agl_solitaire.settings import Settings
from src.agl_solitaire.task_state import TaskState
from src.agl_solitaire.utils import (print,
                                     input,
                                     _builtin_input,
                                     clear,
                                     Loggable,
                                     pad_sentences,
                                     get_grammar_from_obfuscated_repr)


# maybe something like this?
# class Phase(enum.StrEnum):

# Task lifecycle: (1.A and 1.B can happen in either order)
#     0.  inactive
#     1.A prepared (content generated)
#     1.B active (state being tracked)
#     2.  running
#     3.  inactive

@dataclasses.dataclass
class Task(Loggable, TaskState):
    """Represents one AGL test to be done by the user, possibly in a series of several.
    This class provides a default implementation that may be overridden by more specific
    custom Tasks."""

    settings: Settings
    grammar:  typing.Optional[Grammar] = None
    active:   bool = False  # is this Task underway (or queued up next)

    def __post_init__(self):
        """If this is the currently active Task, register it in the Settings it belongs to."""
        # this reads kinda backwards but I can't come up with a nicer way to phrase it
        if self.active:
            if self.settings.halted_task is not None:
                self.resume(self.settings.halted_task)
            self.activate()

    def activate(self):
        """Set this as the Task currently being (or about to be) performed. Keep track of
        its state in the corresponding Settings object too."""
        self.settings.halted_task = self
        self.active = True

    def deactivate(self):
        """Stop tracking the state of this Task in the Settings object."""
        # sic: keep last Task in Settings in case user wants to repeat it
        #self.settings.halted_task = None
        self.active = False

    def resume(self, task_state):
        """Take up a previously halted Task to proceed with it later."""
        for field in dataclasses.fields(TaskState):
            value = getattr(task_state, field.name)
            setattr(self, field.name, value)

    def prepare(self):
        """Populate training and test sets with output generated by our grammar."""
        if self.ready():
            return True
        assert 0 < self.settings.training_strings
        assert 0 < self.settings.test_strings_grammatical
        assert 0 < self.settings.test_strings_ungrammatical
        if not self.grammar:
            self.grammar = get_grammar_from_obfuscated_repr(self.settings)
        num_required_grammatical = self.settings.training_strings + self.settings.test_strings_grammatical
        if not self.settings.grammar_class.custom():
            grammatical_strings = self.grammar.produce_grammatical(num_strings=num_required_grammatical,
                                                                   min_length=self.settings.minimum_string_length,
                                                                   max_length=self.settings.maximum_string_length)
        else:
            grammatical_strings = self.grammar.produce_grammatical(num_strings=num_required_grammatical)
        if grammatical_strings is None:
            return False
        grammatical_strings = list(grammatical_strings)
        if not self.settings.grammar_class.custom():
            ungrammatical_strings = self.grammar.produce_ungrammatical(num_strings=self.settings.test_strings_ungrammatical,
                                                                       min_length=self.settings.minimum_string_length,
                                                                       max_length=self.settings.maximum_string_length)
        else:
            ungrammatical_strings = self.grammar.produce_ungrammatical(num_strings=self.settings.test_strings_ungrammatical)
        # partition grammatical_strings into two subsets
        picked_for_training = random.sample(range(0,num_required_grammatical), k=self.settings.training_strings)
        self.training_set = [grammatical_strings[i] for i in picked_for_training]
        self.test_set = [(grammatical_strings[i], 'y', None) for i in set(range(0,num_required_grammatical)) - set(picked_for_training)]
        self.test_set += [(string, 'n', None) for string in ungrammatical_strings]
        if type(grammatical_strings[0]) is tuple:
            # we got pairs of (form, meaning) from the grammar
            assert all(type(string) is tuple for string in grammatical_strings)
            assert all(type(string) is tuple for string in ungrammatical_strings)
            self.training_set = pad_sentences(self.training_set)
            test_strings = [string for string, _, _ in self.test_set]
            test_answers = [(right, user) for _, right, user in self.test_set]
            self.test_set = [(string, right, user) for (string, (right, user)) in zip(pad_sentences(test_strings), test_answers)]
        else:
            # we got plain strings
            assert all(type(string) is str for string in grammatical_strings)
            assert all(type(string) is str for string in ungrammatical_strings)
        assert len(self.test_set) == self.settings.test_strings_grammatical + self.settings.test_strings_ungrammatical
        # permute test set
        random.shuffle(self.test_set)
        return True

    def ready(self):
        """Check if training and test sets have been populated."""
        if len(self.training_set) != self.settings.training_strings:
            return False
        if len(self.test_set) != self.settings.test_strings_grammatical + self.settings.test_strings_ungrammatical:
            return False
        return True

    def run(self):
        """Let the user perform this generated task."""
        assert self.ready()
        self.activate()
        # used for sleeping but keeping the keyboard awake
        input_thread = None
        if not self.training_finished:
            if self.settings.training_one_at_a_time:
                the_same = 'the same ' if 1 < self.settings.training_reps else ''
                in_rounds = f"in {self.settings.training_reps} rounds " if 1 < self.settings.training_reps else ''
                time_per_item = round(float(self.settings.training_time) / self.settings.training_strings, 2)
                self.duplicate_print(f"The training phase will now begin. You will be presented with {the_same}{self.settings.training_strings} exemplars of the hidden grammar {in_rounds}for {time_per_item} seconds each.")
            else:
                self.duplicate_print(f"The training phase will now begin. You will have {self.settings.training_time} seconds to study a list of {self.settings.training_strings} exemplars of the hidden grammar.")
            self.duplicate_print('You can use Ctrl-Break on Windows or Ctrl-C on macOS/Unix to halt the experiment at any time.')
            self.duplicate_print('Please make sure your screen and terminal font are comfortable to read. Press return when you are ready.')
            input()
            if self.settings.training_one_at_a_time:
                for training_rep in range(1, self.settings.training_reps + 1):
                    for string in self.training_set:
                        clear()
                        print()
                        self.duplicate_print(string)
                        time.sleep(float(self.settings.training_time) / self.settings.training_strings)
                    if training_rep < self.settings.training_reps:
                        clear()
                        self.duplicate_print(f"Round {training_rep} out of {self.settings.training_reps} done. Press return to start round {training_rep+1}.")
                        input()
            else:
                self.duplicate_print('Training phase started. Please study the following list of strings:')
                print()
                self.duplicate_print('\n'.join(self.training_set))
                print()
                input_thread = threading.Thread(target=_builtin_input, daemon=True)
                input_thread.start()
                remaining_time = self.settings.training_time
                while input_thread.is_alive() and 0 < remaining_time:
                    print(f"\r{remaining_time} seconds remaining (press return to finish early)...  ", end='')
                    time.sleep(1)
                    remaining_time -= 1
            print('\rTraining phase finished.' + ' ' * 30)
            self.duplicate_print('Training phase finished.', log_only=True)
            self.training_finished = True
            clear()
        self.duplicate_print(f"The test phase will now begin. You will be shown {len(self.test_set)} new strings one at a time and prompted to judge the grammaticality of each.")
        self.duplicate_print(f"You can use Ctrl-Break on Windows or Ctrl-C on macOS/Unix to halt the experiment at any time. Your progress will be saved to '{self.settings.filename}' and you will be able to finish the experiment later.")
        self.duplicate_print("You may type 'y' for yes (i.e. grammatical) and 'n' for no (ungrammatical). Press return when you are ready.")
        # recycle input_thread if it's still running...
        if input_thread and input_thread.is_alive():
            input_thread.join()
        else:
            input()
        # N.B. you can't do the following because you want to update the original test_set
        #for i, item in enumerate(self.test_set):
        for i in range(len(self.test_set)):
            if self.test_set[i][2] is not None:
                # already answered in a previous session
                continue
            clear()
            self.duplicate_print(f"Test item #{i+1} out of {len(self.test_set)}. Is the following string grammatical? (y/n)")
            print()
            self.duplicate_print(self.test_set[i][0])
            answer = '_'
            while answer[0] not in ['y', 'n']:
                answer = None
                while not answer:
                    answer = input()
                answer = answer[0].lower()
                if answer == 'g':
                    answer = 'y'
                elif answer == 'u':
                    answer = 'n'
            self.duplicate_print(answer, log_only=True)
            self.test_set[i] = (self.test_set[i][0], self.test_set[i][1], answer)
            # FIXME: need to call this manually because __setattr__ doesn't get called if you update a member variable in-place :(
            self.settings.save_all()
        clear()
        self.duplicate_print('Test phase finished. Hope you had fun!')
        self.deactivate()

    def cleanup(self):
        """Tie up any loose ends in terms of resources if we had to abandon the experiment
        early in the middle of Task.run (e.g. because the user halted the experiment)."""
        pass

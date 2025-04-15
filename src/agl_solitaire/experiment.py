"""High-level control of task sequencing in the experiment procedure, I guess."""

import dataclasses
import random

from src.agl_solitaire import settings
from src.agl_solitaire import task
from src.agl_solitaire.utils import print, input, clear, get_grammar_from_obfuscated_repr, Loggable


@dataclasses.dataclass
class Experiment(Loggable):
    """Container for one or more Tasks, responsible for preparing and running them."""

    settings:   settings.Settings
    tasks:      list[task.Task] = dataclasses.field(default_factory = lambda: [])
    tasks_done: int = 0

    # TODO:
    #recommended_settings = None
    # N.B.: class variable, not an object variable
    settings_used = settings.SettingsEnabled()

    def __post_init__(self):
        """By default, create one vanilla default task, unless there's a paused task from before."""
        self.tasks.append(task.Task(settings=self.settings, active=True))

    def prepare(self):
        """Load all tasks with concrete generated material."""
        for task in self.tasks:
            ### ### ### ### ### ###
            success = task.prepare()
            ### ### ### ### ### ###
            if not success:
                return False
        random.shuffle(self.tasks)
        return True

    def ready(self):
        """Has the experiment been adequately prepared so that it's ready to be run?"""
        return all(t.ready() for t in self.tasks[self.tasks_done:])

    def run(self):
        """Let the user perform all tasks of the experiment in order."""
        remaining_tasks = self.tasks[self.tasks_done:]
        for i, task in enumerate(remaining_tasks):
            if 1 < len(self.tasks):
                clear()
                self.duplicate_print(f"***  Welcome to Challenge #{i+1} out of {len(self.tasks)}  ***\n")
            ### ### ### ### ### ###
            task.run()
            ### ### ### ### ### ###
            self.tasks_done += 1
            if self.settings.run_questionnaire:
                self.duplicate_print('A few more questions if you feel like it:')
                self.duplicate_print('Did you feel like you got the hang of the grammar or were you just guessing?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
                self.duplicate_print('Do you feel like you did well in this session?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
                self.duplicate_print('Did you seem to find any concrete giveaways or hints in the strings?')
                answer = input()
                self.duplicate_print(answer, log_only=True)
            clear()
            if not self.settings.grammar_class.custom() and self.settings.grammar is not None:
                self.duplicate_print(f"And now for the big reveal... Strings were generated using the following {self.settings.grammar_class} grammar:")
                gmr = get_grammar_from_obfuscated_repr(self.settings)
                self.duplicate_print(str(gmr))
            correct = sum(item[1] == item[2] for item in task.test_set)
            self.duplicate_print(f"You gave {correct} correct answers out of {len(task.test_set)} ({100 * correct/len(task.test_set):.0f}%). The answers were the following:")
            # make table columns wider if needed
            width = max(16, 2 + max(len(item[0]) for item in task.test_set))
            self.duplicate_print(f"{'Test string':<{width}}{'Correct answer':<16}{'Your answer':<16}")
            for item in task.test_set:
                self.duplicate_print(f"{item[0]:<{width}}{'yes' if 'y' == item[1] else 'no':<16}{'yes' if 'y' == item[2] else 'no':<16}")
            self.duplicate_print('You now have a chance to add any other post hoc notes or comments for the record if you wish. Please enter an empty line when you\'re done:')
            comments = '\n'.join(iter(input, ''))
            self.duplicate_print(comments, log_only=True)

    def cleanup(self):
        """Tie up any loose ends in terms of resources if we had to abandon the experiment
        early in the middle of Task.run (e.g. because the user halted the experiment)."""
        pass

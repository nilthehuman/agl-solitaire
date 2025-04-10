"""High-level control of task sequencing in the experiment procedure, I guess."""

import dataclasses
import typing

from src.agl_solitaire import settings
from src.agl_solitaire import task
from src.agl_solitaire.utils import print, input, clear, get_grammar_from_obfuscated_repr, Loggable


@dataclasses.dataclass
class Experiment:
    """Container for one or more Tasks, responsible for preparing and running them."""

    settings: settings.Settings
    tasks:    list[task.Task] = dataclasses.field(default_factory = lambda: [])

    # N.B.: class variable, not an object variable
    settings_used = settings.SettingsEnabled()

    def __post_init__(self):
        """By default, create one vanilla default task."""
        self.tasks.append(task.Task(self.settings))

    def prepare(self):
        """Load all tasks with concrete generated material."""
        all_good = True
        for task in self.tasks:
            success = task.prepare()
            all_good = all_good and success
        return all_good

    def run(self):
        """Let the user perform all tasks of the experiment in order."""
        for task in self.tasks:
            task.run()

    def cleanup(self):
        """Tie up any loose ends in terms of resources if we had to abandon the experiment
        early in the middle of Task.run (e.g. because the user halted the experiment)."""
        pass

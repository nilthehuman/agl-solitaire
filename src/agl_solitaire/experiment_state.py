"""Class to keep track of the progress of an ongoing experiment session."""

import dataclasses
import typing

# from src.agl_solitaire import settings

@dataclasses.dataclass
class ExperimentState:
    """Current state of an experiment procedure, used to persistently save user's progress midway through."""
    settings:          typing.Optional[None] = None  # alas we cannot refer to the Settings type here :/
    tasks_finished:    int = 0
    training_finished: bool = False
    training_set:      list[str] = dataclasses.field(default_factory = lambda: [])
    test_set:          list[(str, bool, typing.Optional[bool])] = dataclasses.field(default_factory = lambda: [])

    def __getstate__(self):
        state = dict(self.__dict__)
        # avoid pickling the settings reference
        try:
            del state['settings']
        except KeyError:
            # nevermind
            pass
        return state

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # propagate our changes to the owner object
        try:
            if self.settings.autosave:
                self.settings.save_all()
        except AttributeError:
            # no self.settings set yet
            pass


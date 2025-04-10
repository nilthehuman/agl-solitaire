"""Class to keep track of the progress of an ongoing experiment session."""

import dataclasses
import typing


@dataclasses.dataclass
class TaskState:
    """Current state of an ongoing task, used to persistently save user's progress midway through."""

    settings:     None = None  # alas we cannot refer to the Settings type here :/
    training_finished: bool = False
    training_set: list[str] = dataclasses.field(default_factory = lambda: [])
    test_set:     list[(str, bool, typing.Optional[bool])] = dataclasses.field(default_factory = lambda: [])

    def __getstate__(self):
        state = dict(self.__dict__)
        # avoid pickling settings and grammar
        try:
            del state['settings']
            del state['grammar']
        except KeyError:
            # nevermind
            pass
        return state

    def __setattr__(self, name, value):
        notify_settings = True
        try:
            if self.settings is None:
                # settings hasn't been set yet
                notify_settings = False
        except AttributeError:
            # we haven't been properly initialized
            notify_settings = False
        super().__setattr__(name, value)
        if notify_settings and self is self.settings.halted_task:
            # propagate our changes to the owner object
            if self.settings.autosave:
                self.settings.save_all()

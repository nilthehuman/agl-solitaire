"""Classes to keep track of the progress of an ongoing experiment session."""

import dataclasses
import typing

# from src.agl_solitaire import settings

@dataclasses.dataclass
class TaskState:
    """Current state of an ongoing task, used to persistently save user's progress midway through."""

    settings:     None = None  # alas we cannot refer to the Settings type here :/
    training_finished: bool = False
    training_set: list[str] = dataclasses.field(default_factory = lambda: [])
    test_set:     list[(str, bool, typing.Optional[bool])] = dataclasses.field(default_factory = lambda: [])
    anchored_to_end: bool = False  # is this Task to be performed after the main part

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

    # TODO: refactor to get rid of code duplication
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
        if notify_settings:
            # propagate our changes to the owner object
            if self.settings.autosave:
                self.settings.save_all()


@dataclasses.dataclass
class ExperimentState:
    """Current state of an experiment procedure, used to persistently save user's progress midway through."""

    settings:   typing.Optional[None] = None  # alas we cannot refer to the Settings type here :/
    tasks:      list[TaskState] = dataclasses.field(default_factory = lambda: [])
    tasks_done: int = 0

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
        notify_settings = True
        try:
            if self.settings is None:
                # settings hasn't been set yet
                notify_settings = False
        except AttributeError:
            # we haven't been properly initialized
            notify_settings = False
        super().__setattr__(name, value)
        if notify_settings and self is self.settings.halted_experiment:
            # propagate our changes to the owner object
            if self.settings.autosave:
                self.settings.save_all()

    def active_task(self):
        if not self.tasks:
            return None
        that_task = [t for t in self.tasks if t.active]
        assert 1 == len(that_task)
        return that_task[0]

    def activate_next_task(self):
        assert self.tasks
        assert 0 <= self.tasks_done < len(self.tasks)
        for task in self.tasks:
            task.active = False
        self.tasks[self.tasks_done].active = True

    def ready_to_produce(self):
        """Has a Grammar been created or loaded for each Task that needs one?"""
        return all(t.ready_to_produce() is not None for t in self.tasks[self.tasks_done:])

    def ready_to_run(self):
        """Has the experiment been adequately prepared so that it's ready to be executed?"""
        return all(t.ready_to_run() for t in self.tasks[self.tasks_done:])

    def started(self):
        """Has the experiment been started?"""
        if 0 < self.tasks_done:
            return True
        return not all(answer is None for (_, _, answer) in self.active_task().test_set)

    def finished(self):
        """Has the experiment been started?"""
        return self.tasks_done == len(self.tasks)

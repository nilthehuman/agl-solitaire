"""Unit tests to check basic expected behaviors about tracking Experiment state."""

import os.path

from src.agl_solitaire import experiment, task, settings


_TEST_SETTINGS_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '__test_settings__.ini'))
_NEW_SETTINGS = lambda: settings.Settings(filename=_TEST_SETTINGS_PATH)


def test_settings_equality():
    """See if two brand new Settingses are equivalent."""
    s1 = settings.Settings()
    s2 = settings.Settings()
    assert s1.settings_equal(s2)


def test_settings_save_load_roundtrip():
    """See if Settings comes back to the same state from it persisted form."""
    s1 = _NEW_SETTINGS()
    s1.autosave = True
    s1.username = 'abcdefgh'
    s1.training_strings = 42
    s1.recursion = False
    s1.grammar = '__fake__'
    s2 = _NEW_SETTINGS()
    s2.load_all()
    assert s1.settings_equal(s2)


def test_experiment_equality():
    """See if two brand new Experiments are equivalent."""
    s = _NEW_SETTINGS()
    e1 = experiment.Experiment(s)
    e2 = experiment.Experiment(s)
    assert e1 == e2


def test_experiment_save_load_roundtrip():
    """See if an Experiment comes back to the same state from it persisted form."""
    s = _NEW_SETTINGS()
    e1 = experiment.Experiment(s)
    e1.tasks = [task.Task(), task.Task(), task.Task()]
    e1.track_state()
    e1.tasks[0].training_set = ['xyz', 'yzx', 'zxy']
    e1.tasks[0].test_set = [('zyx', True, None)]
    e1.tasks[1].training_set = ['xzy', 'zyx', 'yxz']
    e1.tasks[1].test_set = [('zyx', False, None)]
    e1.tasks[2].training_set = ['yzx', 'zxy', 'xyz']
    e1.tasks[2].test_set = [('zyx', True, None)]
    e2 = experiment.Experiment(s)
    e2.resume(e1)
    assert e1 == e2


def test_experiment_track_progress():
    """See if changes to the state of an Experiment's Tasks get registered by its Settings."""
    s = _NEW_SETTINGS()
    e1 = experiment.Experiment(s)
    e1.tasks = [task.Task(), task.Task(), task.Task()]
    e1.set_settings(s)
    e1.track_state()
    assert not e1.tasks[0].training_finished
    assert not e1.tasks[0].training_set
    assert not e1.tasks[0].test_set
    e1.tasks[0].training_finished = True
    e1.tasks[0].training_set = ['xyz', 'yzx', 'zxy']
    e1.tasks[0].test_set = [('zyx', True, None)]
    e1.tasks[1].training_set = ['xzy', 'zyx', 'yxz']
    e1.tasks[1].test_set = [('zyx', False, None)]
    e1.tasks[2].training_set = ['yzx', 'zxy', 'xyz']
    e1.tasks[2].test_set = [('zyx', True, None)]
    e1.tasks[0].test_set = [('zyx', True, False)]
    e2 = experiment.Experiment(s)
    e2.resume(s.halted_experiment)
    assert e2.tasks[0].training_finished
    assert e2.tasks[0].test_set == [('zyx', True, False)]

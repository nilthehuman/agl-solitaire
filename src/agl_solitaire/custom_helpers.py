"""Utilities for finding and enumerating the custom experiment scripts, found in a dedicated directory."""

import importlib
import os
import pathlib
import sys


CUSTOM_DIR = pathlib.Path(os.path.dirname(__file__)) / 'custom'
CUSTOM_MODULE_PREFIX = 'src.agl_solitaire.custom.'


def get_custom_experiment_filenames():
    def pick(filename):
        return pathlib.Path(filename).suffix == '.py' and '__' not in filename
    try:
        return [filename for filename in os.listdir(CUSTOM_DIR) if pick(filename)]
    except FileNotFoundError:
        return []

def get_custom_experiment_names():
    custom_filenames = get_custom_experiment_filenames()
    return [pathlib.Path(filename).stem for filename in custom_filenames]

def has_custom_experiment(module_name):
    """Is there a CustomExperiment class defined in this module?"""
    try:
        sys.modules[CUSTOM_MODULE_PREFIX + module_name].CustomExperiment
        return True
    except AttributeError:
        return False

def load_custom_experiments():
    custom_exp_names = get_custom_experiment_names()
    valid_custom_exp_names = []
    for name in custom_exp_names:
        try:
            importlib.import_module(CUSTOM_MODULE_PREFIX + name)
        except ModuleNotFoundError:
            raise ModuleNotFoundError('failed to load custom experiment: ' + name)
        if has_custom_experiment(name):
            valid_custom_exp_names.append(name)
    return valid_custom_exp_names

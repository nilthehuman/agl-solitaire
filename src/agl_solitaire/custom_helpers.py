"""Utilities for finding and enumerating the custom experiment scripts, found in their own directory."""

import importlib
import os
import pathlib


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

def load_custom_experiments():
    custom_exp_names = get_custom_experiment_names()
    for name in custom_exp_names:
        try:
            importlib.import_module(CUSTOM_MODULE_PREFIX + name)
        except ModuleNotFoundError:
            raise ModuleNotFoundError('failed to load custom experiment: ' + name)
    return custom_exp_names

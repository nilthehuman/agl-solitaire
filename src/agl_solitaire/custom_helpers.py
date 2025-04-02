"""Utilities for finding and enumerating the custom experiment scripts, found in their own directory."""

import importlib
import os
import pathlib


CUSTOM_DIR = pathlib.Path(os.path.dirname(__file__)) / 'custom'


def get_custom_experiment_filenames():
    return [filename for filename in os.listdir(CUSTOM_DIR) if pathlib.Path(filename).suffix == '.py' and '__' not in filename]

def get_custom_experiment_names():
    custom_filenames = get_custom_experiment_filenames()
    return [pathlib.Path(filename).stem for filename in custom_filenames]


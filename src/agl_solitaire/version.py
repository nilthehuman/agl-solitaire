"""Peek in the setup.cfg file to find out the current version of the application."""

import configparser
from os.path import dirname, join

def get_version():
    """Return this application's current version number."""
    config = configparser.ConfigParser()
    filename = join(dirname(__file__), '..', '..', 'setup.cfg')
    config.read(filename)
    return config['metadata']['version']

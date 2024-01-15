"""Peek in the setup.cfg file to find out the current version of the application."""

import configparser

def get_version():
    """Return this application's current version number."""
    config = configparser.ConfigParser()
    filename = 'setup.cfg'
    config.read(filename)
    return config['metadata']['version']

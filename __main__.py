#!/usr/bin/env python3

from sys import argv

from src.agl_solitaire.application import Application
from src.agl_solitaire.version import get_version

def help():
    """Explain each configuration option in the application in a bit of detail and quit."""
    my_version = get_version()
    print('agl-solitaire ' + my_version + '\n')
    print('Terminal-based tool for running Artificial Grammar Learning experiments.\n')
    print('You can change the following settings in the application to configure your experiments.')
    print('Note that not all settings are applicable to all kinds of grammars or experiments.')
    settings = {
        'username' : 'recorded in the experiment logs, no other purpose than to tell participants apart.\nYou may choose any string you judge suitable to identify you as a participant.',
        'grammar class' : 'the type of grammar or experiment you want to use.\nMay be a regular (type-3) grammar, a kind of finite grammar called "pattern",\nor any of the custom experiments in the src/agl_solitaire/custom/ directory.',
        'number of training strings' : 'how many unique stimuli to use in the training phase.',
        'time allotted for training' : 'total number of seconds the application allows the participant\nto look at the training stimuli.',
        'number of grammatical test strings' : 'how many unique stimuli, acceptable according to\nthe hidden grammar, to use in the test phase.',
        'number of ungrammatical test strings' : 'how many unique stimuli, *not* acceptable according to\nthe hidden grammar, to use in the test phase.',
        'minimum string length' : 'lower bound on number of tokens all training and test stimuli need to be made up of.',
        'maximum string length' : 'upper bound on number of tokens all training and test stimuli need to be made up of.',
        'letters or words to use in strings' : 'the set of basic tokens that may appear in the training and test stimuli.',
        'allow recursion' : 'allow regular grammars with one or more loops (i.e. cycles) in them to be generated.',
        'logfile to record sessions in' : 'the application saves all stimuli and answers in the text file with this filename.',
        'show training strings one at a time' : 'present each training stimulus to the participant for a short time separately.',
        'number of training repetitions' : 'how many times to display the list of training stimuli (in the same order).',
        'run pre and post session questionnaire' : 'ask the participant a few basic questions about facts that might affect their performance,\nas well as their impression of the experiment after the fact.',
        'automatically email logs to author' : 'allow sending the newest segment of experiment log file to the author\nof the application once it\'s completed.'
    }
    def pretty_print(name, descr):
        print('\n' + name + ': ', end='')
        descr_lines = descr.split('\n')
        print(descr_lines[0])
        for line in descr_lines[1:]:
            print((len(name) + 2) * ' ' + line)
    for name, descr in settings.items():
        pretty_print(name, descr)

def main():
    """Run the application."""
    Application().main_menu()

if __name__ == "__main__":
    if 1 < len(argv) and argv[1] in ['-h', '--help']:
        help()
    else:
        main()

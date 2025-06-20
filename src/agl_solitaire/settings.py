"""Save, load and configure persistent user preferences for the AGL experiment paradigm."""

import configparser
import dataclasses
try:
    import dill as pickle
except ImportError:
    import pickle
import enum
import os.path
import sys
try:
    import tomllib
    _TOMLLIB_AVAILABLE = True
except ImportError:
    _TOMLLIB_AVAILABLE = False
import typing


from src.agl_solitaire import custom_helpers
from src.agl_solitaire import version
from src.agl_solitaire.experiment_state import ExperimentState


_PROJECT_ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
_DEFAULT_INI_FILENAME  = os.path.join(_PROJECT_ROOT_DIR, 'settings.ini')
_DEFAULT_TOML_FILENAME = os.path.join(_PROJECT_ROOT_DIR, 'settings.toml')


GrammarClass = enum.StrEnum('GrammarClass', {name:name.lower() for name in ['REGULAR', 'PATTERN']} | {name:name for name in custom_helpers.get_custom_experiment_names()})
GrammarClass.custom = lambda self: self.name.lower() not in ['regular', 'pattern']
def _next_gc(self):
    gc_names = [name for name in GrammarClass]
    i = gc_names.index(self)
    i = (i + 1) % len(gc_names)
    next_name = gc_names[i]
    # avoid selecting an invalid custom grammar class
    while next_name.custom() and not custom_helpers.has_custom_experiment(next_name):
        i = (i + 1) % len(gc_names)
        next_name = gc_names[i]
    return next_name
GrammarClass.next = _next_gc


# TODO: split this into a leaner Settings base class and an ExperimentSession derived class
@dataclasses.dataclass
class Settings:
    """User options for controlling the details of the experimental paradigm."""

    class VersionException(Exception):
        def __init__(self):
            super().__init__('warning: settings file is from an older version of the application, this does not bode well for loading previous experiments\n')

    filename:                   typing.Optional[str] = None
    version:                    str = version.get_version()
    autosave:                   bool = False
    username:                   str = 'anonymous'
    grammar_class:              GrammarClass = GrammarClass.REGULAR
    training_strings:           int = 15
    training_time:              int = 180
    training_reps:              int = 1
    test_strings_grammatical:   int = 5
    test_strings_ungrammatical: int = 5
    minimum_string_length:      int = 2
    maximum_string_length:      int = 8
    string_tokens:              list[str] = dataclasses.field(default_factory = lambda: ['M', 'R', 'S', 'V', 'X'])
    recursion:                  bool = True
    # idea: test_strings_reuse_from_training?
    logfile_filename:           str = 'agl_sessions.log'
    training_one_at_a_time:     bool = False
    run_questionnaire:          bool = True
    email_logs:                 bool = True
    highlight_color:            str = 'default'
    grammar:                    typing.Optional[str] = None
    halted_experiment:          typing.Optional[ExperimentState] = None

    HOUSEKEEPING_MEMBERS = ['filename', 'grammar', 'halted_experiment', 'autosave']

    def settings_equal(self, other):
        """Check if all options are equal except irrelevant ones."""
        for field in dataclasses.fields(self):
            if field.name in Settings.HOUSEKEEPING_MEMBERS:
                continue
            if getattr(self, field.name) != getattr(other, field.name):
                return False
        return True

    def override(self, other):
        """Replace our settings, but not the grammar or the experiment state, with the other object's settings."""
        for field in dataclasses.fields(self):
            if field.name in Settings.HOUSEKEEPING_MEMBERS:
                continue
            setattr(self, field.name, getattr(other, field.name))

    def __str__(self):
        """Print all settings in an .ini config file format."""
        str_repr = ''
        for field in dataclasses.fields(self):
            str_repr += f"{field.name}: {getattr(self, field.name)}\n"
        return str_repr

    def pretty_print(self):
        """Print all settings in an even more conveniently readable format."""
        settings_used = SettingsEnabled()
        if self.grammar_class.custom():
            mod = sys.modules[custom_helpers.CUSTOM_MODULE_PREFIX + self.grammar_class.name]
            settings_used = mod.CustomExperiment.settings_used
        pretty = ''
        pretty += f"Username: {self.username}\n"
        pretty += f"Grammar class: {self.grammar_class}\n"
        if settings_used.training_strings:
            pretty += f"Number of training strings: {self.training_strings}\n"
        if settings_used.training_time:
            pretty += f"Time allotted for training: {self.training_time}\n"
        if settings_used.test_strings_grammatical:
            pretty += f"Number of grammatical test strings: {self.test_strings_grammatical}\n"
        if settings_used.test_strings_ungrammatical:
            pretty += f"Number of ungrammatical test strings: {self.test_strings_ungrammatical}\n"
        if settings_used.minimum_string_length:
            pretty += f"Minimum string length: {self.minimum_string_length}\n"
        if settings_used.maximum_string_length:
            pretty += f"Maximum string length: {self.maximum_string_length}\n"
        if settings_used.string_tokens:
            pretty += f"Tokens to use in strings: {self.string_tokens}\n"
        if settings_used.recursion:
            pretty += f"Recursion allowed in grammar: {self.recursion}\n"
        pretty += f"Logfile to record session in: {self.logfile_filename}\n"
        if settings_used.training_one_at_a_time:
            pretty += f"Show training strings one at a time: {self.training_one_at_a_time}\n"
        if settings_used.training_reps and self.training_one_at_a_time:
            pretty += f"Number of training rounds: {self.training_reps}\n"
        pretty += f"Run pre and post session questionnaire: {self.run_questionnaire}\n"
        pretty += f"Automatically email logs to author: {self.email_logs}\n"
        return pretty

    def pretty_short(self):
        """Only print settings relevant with a grammar loaded from file."""
        settings_used = SettingsEnabled()
        if self.grammar_class.custom():
            mod = sys.modules[custom_helpers.CUSTOM_MODULE_PREFIX + self.grammar_class.name]
            settings_used = mod.CustomExperiment.settings_used
        pretty = ''
        pretty += f"Username: {self.username}\n"
        if settings_used.training_strings:
            pretty += f"Number of training strings: {self.training_strings}\n"
        if settings_used.training_time:
            pretty += f"Time allotted for training: {self.training_time}\n"
        if settings_used.test_strings_grammatical:
            pretty += f"Number of grammatical test strings: {self.test_strings_grammatical}\n"
        if settings_used.test_strings_ungrammatical:
            pretty += f"Number of ungrammatical test strings: {self.test_strings_ungrammatical}\n"
        pretty += f"Logfile to record session in: {self.logfile_filename}\n"
        if settings_used.training_one_at_a_time:
            pretty += f"Show training strings one at a time: {self.training_one_at_a_time}\n"
        if settings_used.training_reps and self.training_one_at_a_time:
            pretty += f"Number of training rounds: {self.training_reps}\n"
        pretty += f"Run pre and post session questionnaire: {self.run_questionnaire}\n"
        return pretty

    def diff(self, other):
        """Show our settings whose values are different from those in other."""
        diff = ''
        # I could really use a macro here
        if self.grammar_class != other.grammar_class:
            diff += f"Grammar class: {self.grammar_class}\n"
        if self.training_strings != other.training_strings:
            diff += f"Number of training strings: {self.training_strings}\n"
        if self.training_time != other.training_time:
            diff += f"Time allotted for training: {self.training_time}\n"
        if self.test_strings_grammatical != other.test_strings_grammatical:
            diff += f"Number of grammatical test strings: {self.test_strings_grammatical}\n"
        if self.test_strings_ungrammatical != other.test_strings_ungrammatical:
            diff += f"Number of ungrammatical test strings: {self.test_strings_ungrammatical}\n"
        if self.minimum_string_length != other.minimum_string_length:
            diff += f"Minimum string length: {self.minimum_string_length}\n"
        if self.maximum_string_length != other.maximum_string_length:
            diff += f"Maximum string length: {self.maximum_string_length}\n"
        if self.string_tokens != other.string_tokens:
            diff += f"Tokens to use in strings: {self.string_tokens}\n"
        if self.recursion != other.recursion:
            diff += f"Recursion allowed in grammar: {self.recursion}\n"
        if self.logfile_filename != other.logfile_filename:
            diff += f"Logfile to record session in: {self.logfile_filename}\n"
        if self.training_one_at_a_time != other.training_one_at_a_time:
            diff += f"Show training strings one at a time: {self.training_one_at_a_time}\n"
        if self.training_reps != other.training_reps:
            diff += f"Number of training rounds: {self.training_reps}\n"
        return diff

    def process_loaded_entry(self, attr_name, value):
        """Helper method to set a specific member variable based on the value
        loaded from file."""
        try:
            # parse attribute from string
            try:
                parsed_value = type(getattr(self, attr_name))(value)
            except ValueError:
                # invalid value provided in settings file
                # TODO: warn user about this unfortunate predicament
                return
            if attr_name in ['recursion', 'training_one_at_a_time', 'run_questionnaire', 'email_logs']:
                parsed_value = str(value).lower() in ['true', 'yes', '1']
            if 'string_tokens' == attr_name:
                parsed_value = ''.join(value).split()
            setattr(self, attr_name, parsed_value)
        except TypeError:
            # value is None which you cannot cast to
            assert getattr(self, attr_name) is None
            if 'grammar' == attr_name:
                assert isinstance(value, str)
                setattr(self, attr_name, value)
                return
            try:
                # see if this string is really a binary string in disguise
                unpickled_value = pickle.loads(eval(value))
                setattr(self, attr_name, unpickled_value)
                if hasattr(unpickled_value, 'settings') and unpickled_value.settings is None:
                    unpickled_value.set_settings(self)
            except Exception:
                # nevermind
                pass
        except AttributeError:
            pass  # doesn't matter

    def load_all(self, filename=None):
        """Read and set our settings values from file according to format based on its extension."""
        if not filename:
            filename = self.filename
        # FIXME: ugly kludge, but .ini is the "more supported" type anyways
        if not filename:
            filename = os.path.join(_PROJECT_ROOT_DIR, _DEFAULT_INI_FILENAME)
        my_version = self.version
        # figure out format from the tail end of the filename
        if _TOMLLIB_AVAILABLE and 'toml' == os.path.splitext(filename)[1].lower():
            self.load_all_from_toml(filename)
        else:
            # default to old format
            self.load_all_from_ini(filename)
        # check version number
        if my_version and self.version:
            def parse_version(version_string):
                if not version_string:
                    raise ValueError
                version_major = ''
                while '.' != (c := version_string[0]):
                    version_major += c
                    version_string = version_string[1:]
                version_major = int(version_major)
                version_string = version_string[1:]
                version_minor = ''
                while '.' != (c := version_string[0]):
                    version_minor += c
                    version_string = version_string[1:]
                version_minor = int(version_minor)
                return (version_major, version_minor)
            try:
                my_version = parse_version(my_version)
                file_version = parse_version(self.version)
                if my_version[0] > file_version[0] or my_version[1] > file_version[1]:
                    raise Settings.VersionException
            except ValueError:
                # looks like one of the version strings is formatted wrong
                pass

    def load_all_from_ini(self, filename=_DEFAULT_INI_FILENAME):
        """Read and set our settings values from an INI settings file if it exists."""
        self.filename = filename
        config = configparser.ConfigParser()
        config.read(filename)
        for section in config:
            for attr_name in config[section]:
                self.process_loaded_entry(attr_name, config[section][attr_name])
        self.autosave = True

    if _TOMLLIB_AVAILABLE:
        def load_all_from_toml(self, filename=_DEFAULT_TOML_FILENAME):
            """Read and set our settings values from a TOML settings file if it exists."""
            self.filename = filename
            try:
                with open(filename, 'rb') as file:
                    settings_dict = tomllib.load(file)
            except FileNotFoundError:
                return  # alright
            for key in settings_dict:
                if isinstance(settings_dict[key], dict):
                    for subkey in settings_dict[key]:
                        self.process_loaded_entry(subkey, settings_dict[key][subkey])
                else:
                    self.process_loaded_entry(key, settings_dict[key])
            self.autosave = True

    def save_all(self, filename=None):
        """Write the current values of all our member variables to file."""
        if not filename:
            filename = self.filename
        assert filename
        if _TOMLLIB_AVAILABLE and 4 < len(filename) and 'toml' == filename[-4:].lower():
            self.save_all_to_toml(filename)
        else:
            self.save_all_to_ini(filename)

    def save_all_to_ini(self, filename=None):
        """Write the current values of all our member variables to an INI config file."""
        if filename:
            # avoid falling into infinite recursion
            def callback():
                self.filename = filename
            self.without_autosave(callback)
        config = configparser.ConfigParser()
        for field in dataclasses.fields(self):
            if 'filename' == field.name or 'autosave' == field.name:
                continue
            elif 'grammar' == field.name and self.grammar is None:
                continue
            elif 'halted_experiment' == field.name and self.halted_experiment is None:
                continue
            # the string_tokens variable is a list of strings internally
            elif 'string_tokens' == field.name:
                # string_tokens may be a list of strings or a list of individual letters
                string_value = ' '.join(self.string_tokens)
            elif 'halted_experiment' == field.name:
                # serialize to byte string
                string_value = str(pickle.dumps(self.halted_experiment))
            else:
                string_value = str(getattr(self, field.name))
            # configparser will try to interpolate the string and cry
            # if it has a stray % character so we must escape those
            config['DEFAULT'][field.name] = string_value.replace('%', '%%')
        with open(self.filename, 'w', encoding='UTF-8') as configfile:
            config.write(configfile)

    if _TOMLLIB_AVAILABLE:
        def save_all_to_toml(self, filename=None):
            """Write the current values of all our member variables to a TOML config file."""
            if filename:
                self.filename = filename
            with open(self.filename, 'w', encoding='UTF-8') as configfile:
                for field in dataclasses.fields(self):
                    if 'filename' == field.name or 'autosave' == field.name:
                        continue
                    elif 'grammar' == field.name and self.grammar is None:
                        continue
                    elif 'halted_experiment' == field.name and self.halted_experiment is None:
                        continue
                    value = getattr(self, field.name)
                    if 'grammar_class' == field.name:
                        # writing grammar class without quotes causes loading to fail
                        value = str(value)
                    elif 'string_tokens' == field.name:
                        # string_tokens may be a list of strings or a list of individual letters
                        value = ' '.join(self.string_tokens)
                    elif 'halted_experiment' == field.name:
                        # serialize to byte string
                        value = str(pickle.dumps(self.halted_experiment))
                    if isinstance(value, str):
                        # N.B.: can't use repr(value) because Python and TOML treat single quotes
                        # differently: Python interpolates inside single quotes but TOML does not
                        value = value.replace('\\', r'\\')
                        value = value.replace('"', r'\"')
                        value = '"' + value + '"'
                    # 'true' and 'false' are lowercase in TOML
                    if isinstance(value, bool):
                        value = str(value).lower()
                    value = str(value)
                    configfile.write(field.name + ' = ' + value + '\n')

    def without_autosave(self, callback):
        """Temporarily suspend the autosave functionality."""
        autosave_backup = self.autosave
        self.autosave = False
        callback()
        self.autosave = autosave_backup

    def batched_save(self, callback):
        """Let the callback update a whole bunch of state before we save to file _once_."""
        self.without_autosave(callback)
        if self.autosave:
            self.save_all()

    def mask_unused(self, settings_enabled, mask_value=None):
        """Remove settings that are currently not relevant according to the SettingsEnabled object."""
        for field in dataclasses.fields(self):
            try:
                if not getattr(settings_enabled, field.name):
                    setattr(self, field.name, mask_value)
            except AttributeError:
                assert field.name in Settings.HOUSEKEEPING_MEMBERS

    def __setattr__(self, attr, value):
        """Save any and all settings changes automatically if required."""
        if hasattr(self, attr) and id(getattr(self, attr)) == id(value):
            return
        super().__setattr__(attr, value)
        if attr != 'autosave':
            try:
                if self.autosave:
                    self.save_all()
            except AttributeError:
                pass  # that's fine


### ### ### ### ### ### ### ###

# generate SettingsEnabled class with all options turned into bool
used_settings = [(f.name, bool, True) for f in dataclasses.fields(Settings) if f.name not in Settings.HOUSEKEEPING_MEMBERS]
SettingsEnabled = dataclasses.make_dataclass('SettingsEnabled', used_settings) #, bases=(Settings,))
def _mask_unused(self, other):
    for field in dataclasses.fields(self):
        new_value = getattr(self, field.name) and getattr(other, field.name)
        setattr(self, field.name, new_value)
SettingsEnabled.mask_unused = _mask_unused

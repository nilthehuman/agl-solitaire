"""Save, load and configure persistent user preferences for the AGL experiment paradigm."""

import configparser
import dataclasses
try:
    import dill as pickle
except ImportError:
    import pickle
import enum
try:
    import tomllib
    _TOMLLIB_AVAILABLE = True
except ImportError:
    _TOMLLIB_AVAILABLE = False
import typing


_DEFAULT_INI_FILENAME  = 'settings.ini'
_DEFAULT_TOML_FILENAME = 'settings.toml'


class GrammarClass(enum.StrEnum):
    REGULAR = "regular"
    PATTERN = "pattern"


@dataclasses.dataclass
class ExperimentState:
    """Current state of an experiment procedure, used to persistently save user's progress midway through."""
    training_finished: bool
    training_set:      list[str]
    test_set:          list[(str, bool, typing.Optional[bool])]


@dataclasses.dataclass
class Settings:
    """User options for controlling the details of the experimental paradigm."""
    filename:                   typing.Optional[str] = None
    username:                   str = 'anonymous'
    grammar_class:              GrammarClass = GrammarClass.REGULAR
    training_strings:           int = 20
    training_time:              int = 300
    test_strings_grammatical:   int = 20
    test_strings_ungrammatical: int = 20
    minimum_string_length:      int = 2
    maximum_string_length:      int = 8
    string_tokens:              list[str] = dataclasses.field(default_factory = lambda: ['M', 'R', 'S', 'V', 'X'])
    recursion:                  bool = True
    # idea: test_strings_reuse_from_training?
    logfile_filename:           str = 'agl_sessions.log'
    training_one_at_a_time:     bool = True
    run_questionnaire:          bool = True
    grammar:                    typing.Optional[str] = None
    experiment_state:           typing.Optional[ExperimentState] = None

    def settings_equal(self, other):
        """Check if all options are equal except irrelevant ones."""
        for field in dataclasses.fields(self):
            if field.name in ['filename', 'grammar', 'experiment_state']:
                continue
            if getattr(self, field.name) != getattr(other, field.name):
                return False
        return True

    def __str__(self):
        """Print all settings in an .ini config file format."""
        str_repr = ''
        for field in dataclasses.fields(self):
            str_repr += f"{field.name}: {getattr(self, field.name)}\n"
        return str_repr

    def pretty_print(self):
        """Print all settings in an even more conveniently readable format."""
        pretty = ''
        pretty += f"Username: {self.username}\n"
        pretty += f"Grammar class: {self.grammar_class}\n"
        pretty += f"Number of training strings: {self.training_strings}\n"
        pretty += f"Time allotted for training: {self.training_time}\n"
        pretty += f"Number of grammatical test strings: {self.test_strings_grammatical}\n"
        pretty += f"Number of ungrammatical test strings: {self.test_strings_ungrammatical}\n"
        pretty += f"Minimum string length: {self.minimum_string_length}\n"
        pretty += f"Maximum string length: {self.maximum_string_length}\n"
        pretty += f"Tokens to use in strings: {self.string_tokens}\n"
        pretty += f"Recursion allowed in grammar: {self.recursion}\n"
        pretty += f"Logfile to record session in: {self.logfile_filename}\n"
        pretty += f"Show training strings one at a time: {self.training_one_at_a_time}\n"
        pretty += f"Run pre and post session questionnaire: {self.run_questionnaire}\n"
        return pretty

    def pretty_short(self):
        """Only print settings relevant with a grammar loaded from file."""
        pretty = ''
        pretty += f"Username: {self.username}\n"
        pretty += f"Number of training strings: {self.training_strings}\n"
        pretty += f"Time allotted for training: {self.training_time}\n"
        pretty += f"Number of grammatical test strings: {self.test_strings_grammatical}\n"
        pretty += f"Number of ungrammatical test strings: {self.test_strings_ungrammatical}\n"
        pretty += f"Logfile to record session in: {self.logfile_filename}\n"
        pretty += f"Show training strings one at a time: {self.training_one_at_a_time}\n"
        pretty += f"Run pre and post session questionnaire: {self.run_questionnaire}\n"
        return pretty

    def process_loaded_entry(self, attr_name, value):
        """Helper method to set a specific member variable based on the value
        loaded from file."""
        try:
            # parse attribute from string
            parsed_value = type(getattr(self, attr_name))(value)
            if attr_name in ['recursion', 'training_one_at_a_time', 'run_questionnaire']:
                parsed_value = str(value).lower() in ['true', 'yes', '1']
            if 'string_tokens' == attr_name:
                parsed_value = ''.join(value).split()
            if 'experiment_state' == attr_name:
                # deserialize from byte string
                parsed_value = pickle.loads(eval(value))
            setattr(self, attr_name, parsed_value)
        except TypeError:
            # value is None which you cannot cast to
            assert getattr(self, attr_name) is None
            try:
                # see if this string is really a binary string in disguise
                value = pickle.loads(eval(value))
            except Exception as e:
                # nevermind
                pass
            setattr(self, attr_name, value)
        except AttributeError:
            pass  # doesn't matter

    def load_all(self, filename=None):
        """Read and set our settings values from file according to format based on its extension."""
        if not filename:
            filename = self.filename
        assert filename
        # figure out format from the tail end of the filename
        if _TOMLLIB_AVAILABLE and 4 < len(filename) and 'toml' == filename[-4:].lower():
            self.load_all_from_toml(filename)
        else:
            # default to old format
            self.load_all_from_ini(filename)

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
                if type(settings_dict[key]) is dict:
                    for subkey in settings_dict[key]:
                        self.process_loaded_entry(subkey, settings_dict[key][subkey])
                else:
                    self.process_loaded_entry(key, settings_dict[key])
            self.autosave = True

    def save_all_to_ini(self, filename=None):
        """Write the current values of all our member variables to an INI config file."""
        if filename:
            self.filename = filename
        config = configparser.ConfigParser()
        for field in dataclasses.fields(self):
            if 'filename' == field.name:
                continue
            elif 'grammar' == field.name and self.grammar is None:
                continue
            elif 'experiment_state' == field.name and self.experiment_state is None:
                continue
            # the string_tokens variable is a list of strings internally
            elif 'string_tokens' == field.name:
                # string_tokens may be a list of strings or a list of individual letters
                config['DEFAULT'][field.name] = ' '.join(self.string_tokens)
            elif 'experiment_state' == field.name:
                # serialize to byte string
                config['DEFAULT'][field.name] = str(pickle.dumps(self.experiment_state))
            else:
                # configparser will try to interpolate the string and cry
                # if it has a stray % character so we must escape those
                escaped_str = str(getattr(self, field.name)).replace('%', '%%')
                config['DEFAULT'][field.name] = escaped_str
        with open(self.filename, 'w', encoding='UTF-8') as configfile:
            config.write(configfile)

    if _TOMLLIB_AVAILABLE:
        def save_all_to_toml(self, filename=None):
            """Write the current values of all our member variables to a TOML config file."""
            if filename:
                self.filename = filename
            with open(self.filename, 'w', encoding='UTF-8') as configfile:
                for field in dataclasses.fields(self):
                    if 'filename' == field.name:
                        continue
                    elif 'grammar' == field.name and self.grammar is None:
                        continue
                    elif 'experiment_state' == field.name and self.experiment_state is None:
                        continue
                    value = getattr(self, field.name)
                    # string_tokens may be a list of strings or a list of individual letters
                    if 'string_tokens' == field.name:
                        config['DEFAULT'][field.name] = ' '.join(self.string_tokens)
                    elif 'experiment_state' == field.name:
                        # serialize to byte string
                        config['DEFAULT'][field.name] = str(pickle.dumps(self.experiment_state))
                    if type(value) is str:
                        # N.B.: can't use repr(value) because Python and TOML treat single quotes
                        # differently: Python interpolates inside single quotes but TOML does not
                        value = value.replace('\\', r'\\')
                        value = value.replace('"', r'\"')
                        value = '"' + value + '"'
                    # 'true' and 'false' are lowercase in TOML
                    if type(value) is bool:
                        value = str(value).lower()
                    value = str(value)
                    configfile.write(field.name + ' = ' + value + '\n')

    def without_autosave(self, callback):
        """Temporarily suspend the autosave functionality."""
        autosave_backup = self.autosave
        self.autosave = False
        callback()
        self.autosave = autosave_backup

    def __setattr__(self, attr, value):
        """Save any and all settings changes automatically if required."""
        super().__setattr__(attr, value)
        if attr != 'autosave':
            try:
                if self.autosave:
                    self.save_all_to_ini()
            except AttributeError:
                pass  # that's fine


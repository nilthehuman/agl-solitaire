"""Save, load and configure persistent user preferences for the AGL experiment paradigm."""

import configparser
import dataclasses
try:
    import tomllib
    _TOMLLIB_AVAILABLE = True
except ImportError:
    _TOMLLIB_AVAILABLE = False
import typing


_DEFAULT_INI_FILENAME  = 'settings.ini'
_DEFAULT_TOML_FILENAME = 'settings.toml'


@dataclasses.dataclass
class Settings:
    """User options for controlling the details of the experimental paradigm."""
    username:                   str = 'anonymous'
    training_strings:           int = 20
    training_time:              int = 300
    test_strings_grammatical:   int = 20
    test_strings_ungrammatical: int = 20
    minimum_string_length:      int = 2
    maximum_string_length:      int = 8
    string_letters:             list[str] = dataclasses.field(default_factory = lambda: ['M', 'R', 'S', 'V', 'X'])
    recursion:                  bool = True
    # idea: test_strings_reuse_from_training?
    logfile_filename:           str = 'agl_sessions.log'
    training_one_at_a_time:     bool = True
    run_questionnaire:          bool = True
    grammar:                    typing.Optional[str] = None

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
        pretty += f"Number of training strings: {self.training_strings}\n"
        pretty += f"Time allotted for training: {self.training_time}\n"
        pretty += f"Number of grammatical test strings: {self.test_strings_grammatical}\n"
        pretty += f"Number of ungrammatical test strings: {self.test_strings_ungrammatical}\n"
        pretty += f"Minimum string length: {self.minimum_string_length}\n"
        pretty += f"Maximum string length: {self.maximum_string_length}\n"
        pretty += f"Letters to use in strings: {self.string_letters}\n"
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
            setattr(self, attr_name, parsed_value)
        except TypeError:
            # current grammar is None which you cannot cast to
            assert getattr(self, attr_name) is None
            self.grammar = value
        except AttributeError:
            pass  # doesn't matter

    def load_all(self, filename):
        """Read and set our settings values from file according to format based on its extension."""
        # figure out format from the tail end of the filename
        if _TOMLLIB_AVAILABLE and 4 < len(filename) and 'toml' == filename[-4:].lower():
            self.load_all_from_toml(filename)
        else:
            # default to old format
            self.load_all_from_ini(filename)

    def load_all_from_ini(self, filename=_DEFAULT_INI_FILENAME):
        """Read and set our settings values from an INI settings file if it exists."""
        config = configparser.ConfigParser()
        config.read(filename)
        for section in config:
            for attr_name in config[section]:
                self.process_loaded_entry(attr_name, config[section][attr_name])
        self.autosave = True

    if _TOMLLIB_AVAILABLE:
        def load_all_from_toml(self, filename=_DEFAULT_TOML_FILENAME):
            """Read and set our settings values from a TOML settings file if it exists."""
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

    def save_all_to_ini(self, filename=_DEFAULT_INI_FILENAME):
        """Write the current values of all our member variables to an INI config file."""
        config = configparser.ConfigParser()
        for field in dataclasses.fields(self):
            if 'grammar' == field.name and self.grammar is None:
                continue
            # the string_letters variable is a list of strings internally
            if 'string_letters' == field.name:
                config['DEFAULT'][field.name] = ''.join(self.string_letters)
            else:
                # configparser will try to interpolate the string and cry
                # if it has a stray % character so we must escape those
                escaped_str = str(getattr(self, field.name)).replace('%', '%%')
                config['DEFAULT'][field.name] = escaped_str
        with open(filename, 'w', encoding='UTF-8') as configfile:
            config.write(configfile)

    if _TOMLLIB_AVAILABLE:
        def save_all_to_toml(self, filename=_DEFAULT_TOML_FILENAME):
            """Write the current values of all our member variables to a TOML config file."""
            with open(filename, 'w', encoding='UTF-8') as configfile:
                for field in dataclasses.fields(self):
                    if 'grammar' == field.name and self.grammar is None:
                        continue
                    value = getattr(self, field.name)
                    # the string_letters variable is a list of strings internally
                    if 'string_letters' == field.name:
                        value = ''.join(self.string_letters)
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

    def __setattr__(self, attr, value):
        """Save any and all settings changes automatically if required."""
        super().__setattr__(attr, value)
        if attr != 'autosave':
            try:
                if self.autosave:
                    self.save_all_to_ini()
            except AttributeError:
                pass  # that's fine


"""Save, load and configure persistent user preferences for the AGL experiment paradigm."""

import configparser
import dataclasses


_DEFAULT_SETTINGS_FILENAME = 'settings.ini'


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
    # idea: test_strings_reuse_from_training?
    logfile_filename:           str = 'agl_sessions.log'
    skip_questionnaire:         bool = False

    def __str__(self):
        """Print all settings in a human-readable format."""
        str_repr = ''
        for field in dataclasses.fields(self):
            str_repr += f"{field.name}: {getattr(self, field.name)}\n"
        return str_repr

    def load_all(self, filename=_DEFAULT_SETTINGS_FILENAME):
        """Read and set our settings values from a settings file if it exists."""
        config = configparser.ConfigParser()
        config.read(filename)
        for section in config:
            for attr_name in config[section]:
                try:
                    # parse attribute from string
                    value = type(getattr(self, attr_name))(config[section][attr_name])
                    if 'skip_questionnaire' == attr_name:
                        value = config[section][attr_name].lower() in ['true', 'yes', '1']
                    setattr(self, attr_name, value)
                except AttributeError:
                    pass  # doesn't matter
        self.loaded = True

    def save_all(self, filename=_DEFAULT_SETTINGS_FILENAME):
        """Write the current values of all our member variables to a config file."""
        config = configparser.ConfigParser()
        for field in dataclasses.fields(self):
            # the letters variable needs special treatment
            if ('string_letters' == field.name):
                config['DEFAULT'][field.name] = ''.join(self.string_letters)
            else:
                config['DEFAULT'][field.name] = str(getattr(self, field.name))
        with open(filename, 'w', encoding='UTF-8') as configfile:
            config.write(configfile)

    def __setattr__(self, attr, value):
        """Save any and all settings changes automatically."""
        super().__setattr__(attr, value)
        try:
            if self.loaded:
                self.save_all()
        except AttributeError:
            pass  # that's fine


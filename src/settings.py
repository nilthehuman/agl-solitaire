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
    training_one_at_a_time:     bool = True
    run_questionnaire:          bool = True

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

    def load_all(self, filename=_DEFAULT_SETTINGS_FILENAME):
        """Read and set our settings values from a settings file if it exists."""
        config = configparser.ConfigParser()
        config.read(filename)
        for section in config:
            for attr_name in config[section]:
                try:
                    # parse attribute from string
                    value = type(getattr(self, attr_name))(config[section][attr_name])
                    if attr_name in ['training_one_at_a_time', 'run_questionnaire']:
                        value = config[section][attr_name].lower() in ['true', 'yes', '1']
                    setattr(self, attr_name, value)
                except AttributeError:
                    pass  # doesn't matter
        self.autosave = True

    def save_all(self, filename=_DEFAULT_SETTINGS_FILENAME):
        """Write the current values of all our member variables to a config file."""
        config = configparser.ConfigParser()
        for field in dataclasses.fields(self):
            # the string_letters variable needs special treatment
            if 'string_letters' == field.name:
                config['DEFAULT'][field.name] = ''.join(self.string_letters)
            else:
                config['DEFAULT'][field.name] = str(getattr(self, field.name))
        with open(filename, 'w', encoding='UTF-8') as configfile:
            config.write(configfile)

    def __setattr__(self, attr, value):
        """Save any and all settings changes automatically."""
        super().__setattr__(attr, value)
        if attr != 'autosave':
            try:
                if self.autosave:
                    self.save_all()
            except AttributeError:
                pass  # that's fine


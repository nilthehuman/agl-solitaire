"""The application's user interface including the main menu and the experimental procedure itself."""

import consolemenu
import dataclasses


@dataclasses.dataclass
class Settings:
    training_strings:           int = 20
    test_strings_grammatical:   int = 20
    test_strings_ungrammatical: int = 20


class TweakItem(consolemenu.items.MenuItem):
    """A menu item to adjust numeric or binary settings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Application(consolemenu.ConsoleMenu):
    """..."""

    def __init__(self):
        super().__init__(title='agl-solitaire', subtitle='A terminal-based Artificial Grammar Learning game')
        self.settings = Settings()
        settings_menu = consolemenu.SelectionMenu([f"Number of training strings: {self.settings.training_strings}",
                                                   f"Number of grammatical test strings: {self.settings.test_strings_grammatical}",
                                                   f"Number of ungrammatical test strings: {self.settings.test_strings_ungrammatical}"])
        self.append_item(consolemenu.items.SubmenuItem('Settings', settings_menu, self))

    def run_experiment(self):
        print('run experiment...')
        # TODO


if __name__ == '__main__':
    app = Application()
    app.show()

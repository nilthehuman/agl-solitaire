"""TEMPORARY ONLY! Special abridged variation of the pilot experiment for my supervisor."""

from .pilot import *

class CustomExperiment(Experiment):

    settings_used = SettingsEnabled()
    settings_used.minimum_string_length = False
    settings_used.maximum_string_length = False
    settings_used.string_tokens = False
    settings_used.recursion = False

    my_grammars = [
        AsymmetricArticlesGrammar,
        VerbReduplicationGrammar,
        EchoMorphologyGrammar,
        RhymingGrammar,
        PalindromeDemonstrativeGrammar,
        RecursiveGrammar
    ]

    def ready_to_run(self):
        if len(self.tasks) != len(self.my_grammars) + 1:
            return False
        return super().ready_to_run()

    def __post_init__(self):
        super().__post_init__()
        if self.ready_to_run():
            return
        # remove default Task created by base class
        self.tasks = []
        for grammar, tokens, proper_names in zip(self.my_grammars,
                                                 random.sample(TOKEN_SETS, k=len(self.my_grammars)),
                                                 random.sample(PROPER_NAME_SETS, k=len(self.my_grammars))):
            random.shuffle(tokens)
            # don't shuffle proper_names so we can identify "genders"
            custom_task = CustomTask(settings=self.settings)
            try:
                custom_task.grammar = grammar(tokens=tokens, proper_names=proper_names)
            except TypeError:
                random.shuffle(RHYMES)
                custom_task.grammar = grammar(tokens=tokens, proper_names=proper_names, rhymes=RHYMES)
            self.tasks.append(custom_task)
        assert all(task.grammar is not None for task in self.tasks)
        last_task = NaturalnessJudgementTask(settings=self.settings, anchored_to_end=True)
        self.tasks.append(last_task)
        unanchored_tasks = [t for t in self.tasks if not t.anchored_to_end]
        anchored_tasks   = [t for t in self.tasks if t.anchored_to_end]
        random.shuffle(unanchored_tasks)
        self.tasks = unanchored_tasks + anchored_tasks
        self.tasks[0].active = True

# import abc
# import dataclasses
import itertools
import random
import re

try:
    random.seeded
except AttributeError:
    import time
    random.seed(time.time())


from src.agl_solitaire.grammar import CustomGrammar
from src.agl_solitaire.settings import SettingsEnabled
from src.agl_solitaire.task import Task


TOKEN_SETS = [
    [ 'an', 'ar', 'bobo', 'dal', 'eli', 'kuu', 'mamo', 'mele', 'nu', 'pul', 'teng', 'ze' ],
    [ 'a', 'ava', 'ele', 'il', 'kon', 'moda', 'me', 'punnu', 'shii', 'tam', 'va', 'zen' ],
    [ 'amura', 'es', 'ilani', 'gova', 'khen', 'li', 'oba', 'pol', 'ter', 'to', 'xe', 'zo' ],
    [ 'ado', 'hovo', 'kere', 'loa', 'pavo', 'saso', 'sil', 'tir', 'mod', 'muma', 'nog', 'wa' ],
    [ 'bo', 'bunna', 'ebbe', 'enta', 'haaru', 'kaal', 'ki', 'sawa', 'sor', 'tama', 'tean', 'zaal' ],
    [ 'amo', 'avadi', 'bint', 'esse', 'gorra', 'ikka', 'min', 'mula', 'ol', 'teti', 've', 'voro' ],
    [ 'ateme', 'en', 'felle', 'gora', 'khiad', 'myna', 'mu', 'o', 'soro', 'xind', 'yko', 'ylmo' ],
    [ 'del', 'fy', 'fyyri', 'hel', 'ivi', 'kaha', 'ky', 'ma', 'min', 'porda', 'te', 'wek' ],
    [ 'atta', 'eve', 'henne', 'i', 'manba', 'mene', 'pon', 'raago', 'tor', 'tuu', 'uva', 'zoto' ],
    [ 'cir', 'daa', 'dyn', 'e', 'iti', 'men', 'ogho', 'shen', 'taal', 'urro', 'uzto', 'zeb' ],
    [ 'aa', 'farra', 'ke', 'meze', 'mor', 'ne', 'ni', 'ob', 'ono', 'pur', 'tala', 'toyo' ],
    [ 'aene', 'de', 'er', 'hin', 'lu', 'maata', 'melde', 'nii', 'olta', 'osso', 'pi', 'vent' ]
]
for tokens in TOKEN_SETS:
    assert len(tokens) == 12


def polish_sentence(sentence):
    """Turn a stimulus into its final presentable form."""
    form, meaning = sentence
    # assemble from tuples
    form = ''.join(form)
    meaning = ''.join(meaning)
    # pack superfluous spaces together
    form = re.sub(r"\s+", ' ', form)
    meaning = re.sub(r"\s+", ' ', meaning)
    # make them look like actual sentences
    form = form.capitalize()
    meaning = meaning.capitalize()
    return form + '.\t' + "'" + meaning + ".'"


class NominalAgreementGrammar(CustomGrammar):
    """A grammar fragment where nouns and their adjectives agree in definiteness marking."""

    def __init__(self, tokens):
        super().__init__(tokens)
        self.lexicon = {
            'the'        : self.tokens[0],
            'lazy'       : self.tokens[1],
            'nice'       : self.tokens[2],
            'old'        : self.tokens[3],
            'young'      : self.tokens[4],
            'dog'        : self.tokens[5],
            'man'        : self.tokens[6],
            'woman'      : self.tokens[7],
            'is reading' : self.tokens[8],
            'is running' : self.tokens[9],
            'a lot'      : self.tokens[10],
            'tonight'    : self.tokens[11],
        }

    def produce_grammatical(self, num_sentences, polish=True):
        sentence_pattern_def = [
            [ 'the' ],
            [ 'lazy ', 'nice ', 'old ', 'young ' ],
            [ 'the' ],
            [ 'dog ', 'man ', 'woman ' ],
            [ 'is running', 'is reading' ],
            [ '', ' a lot', ' tonight' ]
        ]
        sentence_pattern_indef = [
            [ 'lazy ', 'nice ', 'old ', 'young ' ],
            [ 'dog ', 'man ', 'woman ' ],
            [ 'is running', 'is reading' ],
            [ '', ' a lot', ' tonight' ]
        ]
        sentences_def = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_def)]
        sentences_def = random.sample(sentences_def, int(num_sentences / 2 + 0.5))
        # Martian is fine, but space needed after English 'the'
        sentences_def = [(mar, (eng[0]+' ', eng[1],) + eng[3:]) for mar, eng in sentences_def]
        sentences_indef = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_indef)]
        sentences_indef = random.sample(sentences_indef, int(num_sentences / 2 + 0.5))
        # Martian is fine, English needs an indefinite article
        sentences_indef = [(mar, ('a' + ('n' if eng[0].startswith('o') else '') + ' ',) + eng) for mar, eng in sentences_indef]
        sentences = sentences_def + sentences_indef
        if polish:
            sentences = [polish_sentence(s) for s in sentences]
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_sentences, polish=True):
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_sentences:
            sentence = self.produce_grammatical(1, polish=False)[0]
            done = False
            form, meaning = sentence
            while not done:
                if random.choice([True, False]):
                    if meaning[0] == 'the ':
                        form = form[0:2] + form[3:]
                    else:
                        form = form[0:1] + (self.translate('the'),) + form[1:]
                    done = True
                if random.choice([True, False]):
                    if meaning[0] == 'the ':
                        form = form[1:]
                    else:
                        form = (self.translate('the'),) + form
                    done = True
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            ungrammatical_sentences = [polish_sentence(s) for s in ungrammatical_sentences]
        return ungrammatical_sentences


class CustomTask(Task):

    settings_used = SettingsEnabled()
    settings_used.minimum_string_length = False
    settings_used.maximum_string_length = False
    settings_used.string_tokens = False
    settings_used.recursion = False

    def run(self):
        tasks = []
        # for...
        tokens = random.choice(TOKEN_SETS)
        random.shuffle(tokens)
        nominal_agr_task = Task(NominalAgreementGrammar(tokens))
        nominal_agr_task.training_set = nominal_agr_task.produce_grammatical(20)
        nominal_agr_task.test_set = nominal_agr_task.produce_grammatical(5) + nominal_agr_task.produce_ungrammatical(5)
        tasks.append(nominal_agr_task)
        # proba :)
        for t in tasks:
            t.run_task()

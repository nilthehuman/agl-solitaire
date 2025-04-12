import itertools
import random
import re

try:
    random.seeded
except AttributeError:
    import time
    random.seed(time.time())


from src.agl_solitaire.experiment import Experiment
from src.agl_solitaire.grammar import CustomGrammar
from src.agl_solitaire.settings import SettingsEnabled
from src.agl_solitaire.task import Task
from src.agl_solitaire.utils import polish_sentences


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
    [ 'ata', 'farra', 'ke', 'meze', 'mor', 'ne', 'ni', 'ob', 'ono', 'pur', 'tala', 'toyo' ],
    [ 'aene', 'de', 'er', 'hin', 'lu', 'maata', 'melde', 'nii', 'olta', 'osso', 'pi', 'vent' ],
    [ 'ar', 'bo', 'da', 'echa', 'me', 'opo', 'oto', 'pau', 'sako', 'tau', 'ti', 'ud' ],
    [ 'ben', 'e', 'far', 'hen', 'huu', 'mi', 'ne', 'op', 'pa', 'ro', 'tel', 'tum' ],
    [ 'ava', 'ethi', 'gar', 'im', 'ippi', 'ka', 'miko', 'og', 'onno', 'pana', 'qon', 'va' ]
]
for tokens in TOKEN_SETS:
    assert len(tokens) == 12


class DefiniteArticleAgreementGrammar(CustomGrammar):
    """A grammar fragment where nouns and their adjectives agree in definiteness marking."""

    def __init__(self, tokens):
        super().__init__(tokens)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[0]):
            random.shuffle(self.tokens)
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

    def produce_grammatical(self, num_strings=1, polish=True):
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
        try:
            sentences_def = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_def)]
            sentences_def = random.sample(sentences_def, int(num_strings / 2 + 0.5))
            # Martian is fine, but space needed after English 'the'
            sentences_def = [(mar, (eng[0]+' ', eng[1],) + eng[3:]) for mar, eng in sentences_def]
            sentences_indef = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_indef)]
            sentences_indef = random.sample(sentences_indef, int(num_strings / 2 + 0.5))
            # Martian is fine, English needs an indefinite article
            sentences_indef = [(mar, ('a' + ('n' if eng[0].startswith('o') else '') + ' ',) + eng) for mar, eng in sentences_indef]
        except ValueError:
            return None
        sentences = sentences_def + sentences_indef
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_strings:
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
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class AccusativeMarkingAgreementGrammar(CustomGrammar):
    """A grammar fragment where nouns and their adjuncts agree in object marking."""

    def __init__(self, tokens):
        super().__init__(tokens)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[4]) or not monosyll(self.tokens[11]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'she'        : self.tokens[0],
            'he'         : self.tokens[1],
            'brought'    : self.tokens[2],
            'found'      : self.tokens[3],
            'a'          : self.tokens[4],
            'two'        : self.tokens[5],
            'good'       : self.tokens[6],
            'large'      : self.tokens[7],
            'basket'     : self.tokens[8],
            'chair'      : self.tokens[9],
            'horse'      : self.tokens[10],
            'ACC'        : self.tokens[11]
        }

    # cool idea: [ 'a ', 'a ', 'a ', 'two ' ],  # skewing determiners' rate of occurrence

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_indef = [
            [ 'she ', 'he ' ],
            [ 'brought ', 'found ' ],
            [ 'a' ],
            [ ' basket', ' chair', ' horse' ],
            [ 'ACC' ]
        ]
        sentence_pattern_quant = [
            [ 'she ', 'he ' ],
            [ 'brought ', 'found ' ],
            [ 'two', 'good', 'large' ],
            [ 'ACC ' ],
            [ ' basket', ' chair', ' horse' ],
            [ 'ACC' ]
        ]
        try:
            sentences_indef = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_indef)]
            sentences_indef = random.sample(sentences_indef, int(num_strings / 2 + 0.5))
            sentences_quant = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_quant)]
            sentences_quant = random.sample(sentences_quant, int(num_strings / 2 + 0.5))
        except ValueError:
            return None
        # erase ACC from the English translations
        sentences_indef = [(mar, eng[:-1]) for mar, eng in sentences_indef]
        sentences_quant = [(mar, eng[0:3] + eng[4:5]) for mar, eng in sentences_quant]
        # Martian is fine, but English needs plurals
        sentences_quant = [(mar, eng[:-1] + (eng[-1]+'s',)) for mar, eng in sentences_quant]
        sentences = sentences_indef + sentences_quant
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            done = False
            form, meaning = sentence
            while not done:
                if random.choice([True, False]):
                    form = form[:-1]
                    done = True
                if random.choice([True, False]):
                    if 'a' == meaning[2]:
                        # indef sentence
                        form = form[0:3] + (self.translate('ACC'),) + form[3:]
                    else:
                        # quant sentence
                        form = form[0:3] + form[4:]
                    done = True
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class VerbalAgreementGrammar(CustomGrammar):
    """A grammar fragment where subjects and verbs agree in gender."""

    def __init__(self, tokens):
        super().__init__(tokens)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while (not monosyll(self.tokens[8]) or not monosyll(self.tokens[9]) or
                   monosyll(self.tokens[10]) or monosyll(self.tokens[11])):
            random.shuffle(self.tokens)
        self.lexicon = {
            'she'         : self.tokens[0],
            'he'          : self.tokens[1],
            'a girl'      : self.tokens[2],
            'a boy'       : self.tokens[3],
            'two girls'   : self.tokens[4] + ' ' + self.tokens[2],
            'two boys'    : self.tokens[4] + ' ' + self.tokens[3],
            'is'          : '',  # fix actual number agreement later on
            'eating'      : self.tokens[6],
            'baking'      : self.tokens[7],
            'FEM'         : self.tokens[8],
            'MASC'        : self.tokens[9],
            'pizza'       : self.tokens[10],
            'a cake'      : self.tokens[11]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_fem = [
            [ 'she ', 'a girl ', 'two girls ' ],
            [ 'is ' ],
            [ 'eating', 'baking' ],
            [ 'FEM' ],
            [ '', ' pizza', ' a cake' ]
        ]
        sentence_pattern_masc = [
            [ 'he ', 'a boy ', 'two boys ' ],
            [ 'is ' ],
            [ 'eating', 'baking' ],
            [ 'MASC' ],
            [ '', ' pizza', ' a cake' ]
        ]
        try:
            sentences_fem = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_fem)]
            sentences_fem = random.sample(sentences_fem, int(num_strings / 2 + 0.5))
            sentences_masc = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_masc)]
            sentences_masc = random.sample(sentences_masc, int(num_strings / 2 + 0.5))
        except ValueError:
            return None
        sentences = sentences_fem + sentences_masc
        # Martian is fine, English needs number agreement
        sentences = [(mar, eng[0:1] + ('are ' if eng[0].startswith('two') else 'is ',) + eng[2:]) for mar, eng in sentences]
        # erase gender markers from the English translations
        sentences = [(mar, eng[0:3] + eng[4:]) for mar, eng in sentences]
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            form, meaning = sentence
            flipped = self.translate('FEM') if form[3] == self.translate('MASC') else self.translate('MASC')
            form = form[0:3] + (flipped,) + form[4:]
            sentence = (form, meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class VerbReduplicationGrammar(CustomGrammar):
    """A grammar fragment where a verb is uttered twice, first before the object and then before an adverb."""

    def __init__(self, tokens):
        super().__init__(tokens)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[11]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'your'      : self.tokens[0],
            'their'     : self.tokens[1],
            'friend'    : self.tokens[2],
            'daughter'  : self.tokens[3],
            'neighbor'  : self.tokens[4],
            'speaks'    : self.tokens[5],
            'plays'     : self.tokens[6],
            'Dutch'     : self.tokens[7].capitalize(),
            'the piano' : self.tokens[8],
            'often'     : self.tokens[9],
            'well'      : self.tokens[10],
            'DE'        : self.tokens[11]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_short = [
            [ 'your ', 'their ' ],
            [ 'friend ', 'daughter ', 'neighbor ' ],
            [ 'speaks ', 'plays ' ],
            [ 'Dutch ', 'the piano ' ]
        ]
        sentence_pattern_long = [
            [ 'your ', 'their ' ],
            [ 'friend ', 'daughter ', 'neighbor ' ],
            [ 'speaks ', 'plays ' ],
            [ 'Dutch ', 'the piano ' ],
            [ 'speaks ', 'plays ' ],
            [ 'DE ' ],
            [ 'often', 'well' ]
        ]
        def object_makes_sense(sentence):
            # let the verbs select for the correct type of object, obviously
            if ((sentence[2] == 'plays '  and sentence[3] == 'the piano ') or
                (sentence[2] == 'speaks ' and sentence[3] == 'Dutch ')):
                try:
                    if sentence[2] == sentence[4]:
                        return True
                    else:
                        return False
                except IndexError:
                    return True
            else:
                return False
        try:
            sentences_short = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_short) if object_makes_sense(s)]
            sentences_short = random.sample(sentences_short, int(num_strings / 2 + 0.5))
            sentences_long = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_long) if object_makes_sense(s)]
            sentences_long = random.sample(sentences_long, int(num_strings / 2 + 0.5))
        except ValueError:
            return None
        # erase reduplication from the English translations
        sentences_long = [(mar, eng[0:4] + eng[6:]) for mar, eng in sentences_long]
        sentences = sentences_short + sentences_long
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            form, meaning = sentence
            if len(form) < 5:
                # short sentence, add a nonsense DE particle
                form = form + (self.translate('DE'),)
            else:
                done = False
                # long sentence, remove at least one of the reduplication bits
                while not done:
                    if random.choice([True, False]):
                        form = form[0:5] + form[6:]
                        done = True
                    if random.choice([True, False]):
                        form = form[0:4] + form[5:]
                        done = True
            sentence = (form, meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class CustomExperiment(Experiment):

    settings_used = SettingsEnabled()
    settings_used.minimum_string_length = False
    settings_used.maximum_string_length = False
    settings_used.string_tokens = False
    settings_used.recursion = False

    def __post_init__(self):
        my_grammars = [
                        VerbReduplicationGrammar,
                        #VerbalAgreementGrammar,
                        #AccusativeMarkingAgreementGrammar,
                        #DefiniteArticleAgreementGrammar
                      ]
        first = True
        for grammar in my_grammars:
            tokens = random.choice(TOKEN_SETS)
            random.shuffle(tokens)
            custom_task = Task(settings=self.settings, active=True if first else False)
            custom_task.grammar = grammar(tokens)
            custom_task.prepare()
            self.tasks.append(custom_task)
            first = False

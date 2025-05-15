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
from src.agl_solitaire.utils import clear, print, input, polish_sentences, Loggable


TOKEN_SETS = [
    [ 'an', 'ar', 'bobo', 'dal', 'eli', 'kuu', 'ma', 'mele', 'nuppi', 'pul', 'teng', 'ze' ],
    [ 'a', 'ele', 'il', 'kon', 'moda', 'me', 'nigi', 'punnu', 'shii', 'tam', 'va', 'zen' ],
    [ 'amura', 'es', 'ilani', 'gova', 'khen', 'li', 'ni', 'oba', 'pol', 'so', 'to', 'xe' ],
    [ 'ado', 'hovo', 'kere', 'loa', 'mod', 'muma', 'nog', 'pavo', 'saso', 'sil', 'tir', 'wa' ],
    [ 'bo', 'bunna', 'ebbe', 'enta', 'haaru', 'ki', 'maja', 'om', 'sawa', 'sor', 'tama', 'zaal' ],
    [ 'amo', 'avadi', 'bint', 'esse', 'gorra', 'ikka', 'mir', 'mula', 'ol', 'teti', 've', 'voro' ],
    [ 'ateme', 'en', 'felle', 'gora', 'khiad', 'myna', 'mu', 'o', 'soro', 'xind', 'yko', 'ylmo' ],
    [ 'del', 'fy', 'fyyri', 'hel', 'ivi', 'kaha', 'ky', 'mamo', 'min', 'porda', 'te', 'wek' ],
    [ 'atta', 'eve', 'henne', 'i', 'manba', 'men', 'pon', 'raago', 'tor', 'tuu', 'uva', 'zoto' ],
    [ 'daa', 'dyn', 'e', 'iti', 'mene', 'nu', 'ogho', 'shen', 'taal', 'urro', 'uzto', 'zo' ],
    [ 'ata', 'cir', 'farra', 'ke', 'meze', 'mor', 'nibi', 'op', 'ono', 'pur', 'tala', 'toyo' ],
    [ 'aene', 'de', 'er', 'hin', 'lu', 'maata', 'melde', 'no', 'olta', 'osso', 'pi', 'vent' ],
    [ 'araz', 'bom', 'da', 'echa', 'mel', 'opo', 'oto', 'pau', 'sako', 'tau', 'ti', 'ud' ],
    [ 'ben', 'ega', 'firno', 'hen', 'huu', 'mi', 'ne', 'opi', 'pa', 'ro', 'tel', 'tum' ],
    [ 'ava', 'eti', 'gar', 'im', 'ka', 'miko', 'na', 'og', 'onno', 'pana', 'quon', 'vu' ],
    [ 'baa', 'ber', 'dem', 'koko', 'mem', 'nuo', 'pin', 'sa', 'sik', 'tan', 'usu', 'yppo' ],
    [ 'baro', 'do', 'hi', 'lo', 'mbe', 'mina', 'ope', 'pek', 'tunde', 'u', 'vym', 'wal' ],
    [ 'am', 'fer', 'ho', 'je', 'mata', 'nin', 'ob', 'pirra', 'samu', 'ten', 'toma', 'wu' ],
    [ 'bevish', 'el', 'go', 'kabu', 'munga', 'milen', 'nau', 'nish', 'ruu', 'ter', 'tin', 'vi' ],
    [ 'anga', 'bara', 'em', 'gii', 'hol', 'lato', 'momma', 'pede', 'polo', 'se', 'tai', 'tu' ],
    [ 'bi', 'chari', 'kol', 'koro', 'maa', 'mbene', 'nga', 'por', 'ru', 'tolo', 'vende', 'ye' ],
    [ 'amma', 'bin', 'choa', 'eze', 'ito', 'keme', 'miz', 'mou', 'po', 'su', 'uk', 'uru' ],
    [ 'arwa', 'den', 'eis', 'gor', 'hei', 'loma', 'megi', 'nam', 're', 'sim', 'tun', 'vagu' ],
    [ 'as', 'be', 'boi', 'dakh', 'hem', 'kel', 'shoka', 'jiba', 'lulu', 'tol', 'vongo', 'ulme' ]
]
for tokens in TOKEN_SETS:
    assert len(tokens) == 12

PROPER_NAME_SETS = [
    [ 'Ammu',    'Baxer' ],
    [ 'Bilka',   'Arno' ],
    [ 'Cenga',   'Dilve' ],
    [ 'Domota',  'Chiras' ],
    [ 'Egevina', 'Fei Li' ],
    [ 'Fendi',   'Enbos' ],
    [ 'Gresta',  'Hiki' ],
    [ 'Hulma',   'Goso' ],
    [ 'Imman',   'Jamu' ],
    [ 'Juchu',   'Ikil' ],
    [ 'Kagora',  'Lem' ],
    [ 'Lasha',   'Kuor' ],
    [ 'Mara',    'Neri' ],
    [ 'Nekki',   'Munlo' ],
    [ 'Onte',    'Pavel' ],
    [ 'Pembosh', 'Ortin' ],
    [ 'Quesse',  'Ruos' ],
    [ 'Rinka',   'Qaal' ],
    [ 'Shen',    'Trevion' ],
    [ 'Tibu',    'Silaq' ],
    [ 'Umida',   'Vinne' ],
    [ 'Venke',   'Umpa' ],
    [ 'Wolnea',  'Xalo' ],
    [ 'Xinebu',  'Wotur' ],
    [ 'Yrris',   'Zog' ],
    [ 'Zigel',   'Yshtu' ]
]

RHYMES = [
    ('borna', 'lorna'), ('fairu', 'tairu'), ('gullam', 'mullam'), ('helto', 'nelto'), ('ippo', 'pippo'),
    ('kolo', 'tolo'), ('mahi', 'vahi'), ('ledek', 'nedek'), ('sendu', 'vendu'), ('tuko', 'zuko')
]


class CustomTask(Task):
    """Our type of task, which has no need for a Grammar."""

    def ready_to_produce(self):
        return True


class DefiniteArticleAgreementGrammar(CustomGrammar):
    """A grammar fragment where nouns and their adjectives agree in definiteness marking."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
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
        sentence_pattern_name = [
            self.proper_names,
            [ ' is running', ' is reading' ],
            [ '', ' a lot', ' tonight' ]
        ]
        try:
            sentences_def = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_def)]
            sentences_def = random.sample(sentences_def, int(num_strings / 3 + 0.67))
            # Martian is fine, but space needed after English 'the'
            sentences_def = [(mar, (eng[0]+' ', eng[1],) + eng[3:]) for mar, eng in sentences_def]
            sentences_indef = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_indef)]
            sentences_indef = random.sample(sentences_indef, int(num_strings / 3 + 0.67))
            # Martian is fine, English needs an indefinite article
            sentences_indef = [(mar, ('a' + ('n' if eng[0].startswith('o') else '') + ' ',) + eng) for mar, eng in sentences_indef]
            sentences_name = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_name)]
            sentences_name = random.sample(sentences_name, int(num_strings / 3 + 0.67))
        except ValueError:
            return None
        sentences = sentences_def + sentences_indef + sentences_name
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
            while True:
                if random.choice([True, False]):
                    if meaning[0] == 'the ':
                        form = form[0:2] + form[3:]
                    else:
                        form = form[0:1] + (self.translate('the'),) + form[1:]
                    break
                elif random.choice([True, False]):
                    if meaning[0] == 'the ':
                        form = form[1:]
                    else:
                        form = (self.translate('the'),) + form
                    break
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class AsymmetricArticlesGrammar(CustomGrammar):
    """A grammar fragment where the definite article cliticizes to the end of the noun head
    but the indefinite article does not."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[0]) or not monosyll(self.tokens[1]) or monosyll(self.tokens[5]) or monosyll(self.tokens[6]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'a'             : self.tokens[0],
            'the'           : self.tokens[1],
            'some'          : '',
            'doctor'        : self.tokens[2],
            'knight'        : self.tokens[3],
            'troll'         : self.tokens[4],
            'drank'         : self.tokens[5],
            'stole'         : self.tokens[6],
            'beer'          : self.tokens[7],
            'coffee'        : self.tokens[8],
            'magic potion'  : self.tokens[9] + self.tokens[10]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_indef_indef = [
            [ 'a ', 'some ' ],
            [ 'doctor', 'knight', 'troll' ],
            [ ' drank ', ' stole ' ],
            [ 'a ', 'some ' ],
            [ 'beer', 'coffee', 'magic potion' ]
        ]
        sentence_pattern_indef_def = [
            [ 'a ', 'some ' ],
            [ 'doctor', 'knight', 'troll' ],
            [ ' drank ', ' stole ' ],
            [ 'beer', 'coffee', 'magic potion' ],
            [ 'the ' ]
        ]
        sentence_pattern_def_indef = [
            [ 'doctor', 'knight', 'troll' ],
            [ 'the ' ],
            [ ' drank ', ' stole ' ],
            [ 'a ', 'some ' ],
            [ 'beer', 'coffee', 'magic potion' ]
        ]
        sentence_pattern_def_def = [
            [ 'doctor', 'knight', 'troll' ],
            [ 'the ' ],
            [ ' drank ', ' stole ' ],
            [ 'beer', 'coffee', 'magic potion' ],
            [ 'the ' ]
        ]
        sentence_pattern_name_indef = [
            self.proper_names,
            [ ' drank ', ' stole ' ],
            [ 'a ', 'some ' ],
            [ 'beer', 'coffee', 'magic potion' ]
        ]
        sentence_pattern_name_def = [
            self.proper_names,
            [ ' drank ', ' stole ' ],
            [ 'beer', 'coffee', 'magic potion' ],
            [ 'the ' ]
        ]
        def finalize_english(string):
            if string[-2:] == ('some ', 'magic potion'):
                return string[:-1] + ('magic potions',)
            return string
        try:
            sentences_indef_indef = [(self.translate(s), finalize_english(s)) for s in itertools.product(*sentence_pattern_indef_indef)]
            sentences_indef_indef = random.sample(sentences_indef_indef, int(num_strings / 4 + 0.25))
            sentences_indef_def = [(self.translate(s), finalize_english(s)) for s in itertools.product(*sentence_pattern_indef_def)]
            sentences_indef_def = random.sample(sentences_indef_def, int(num_strings / 4 + 0.25))
            sentences_def_indef = [(self.translate(s), finalize_english(s)) for s in itertools.product(*sentence_pattern_def_indef)]
            sentences_def_indef = random.sample(sentences_def_indef, int(num_strings / 4 + 0.25))
            sentences_def_def = [(self.translate(s), finalize_english(s)) for s in itertools.product(*sentence_pattern_def_def)]
            sentences_def_def = random.sample(sentences_def_def, int(num_strings / 4 + 0.25))
            sentences_name_indef = [(self.translate(s), finalize_english(s)) for s in itertools.product(*sentence_pattern_name_indef)]
            sentences_name_indef = random.sample(sentences_name_indef, int(num_strings / 4 + 0.25))
            sentences_name_def = [(self.translate(s), finalize_english(s)) for s in itertools.product(*sentence_pattern_name_def)]
            sentences_name_def = random.sample(sentences_name_def, int(num_strings / 4 + 0.25))
        except ValueError:
            return None
        # restore English word order
        sentences_indef_def = [(mar, eng[0:3] + (eng[4],) + (eng[3],)) for mar, eng in sentences_indef_def]
        sentences_def_indef = [(mar, (eng[1],) + (eng[0],) + eng[2:]) for mar, eng in sentences_def_indef]
        sentences_def_def = [(mar, (eng[1], eng[0], eng[2], eng[4], eng[3])) for mar, eng in sentences_def_def]
        sentences_name_def = [(mar, (eng[0], eng[1], eng[3], eng[2])) for mar, eng in sentences_name_def]
        sentences = sentences_indef_indef + sentences_indef_def + sentences_def_indef + sentences_def_def + sentences_name_def
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        bad_pattern_indef_indef = [
            [ 'doctor', 'knight', 'troll' ],
            [ 'a ', 'some ' ],
            [ ' drank ', ' stole ' ],
            [ 'beer', 'coffee', 'magic potion' ],
            [ 'a ', 'some ' ]
        ]
        bad_pattern_indef_def = [
            [ 'doctor', 'knight', 'troll' ],
            [ 'a ', 'some ' ],
            [ ' drank ', ' stole ' ],
            [ 'the ' ],
            [ 'beer', 'coffee', 'magic potion' ]
        ]
        bad_pattern_def_indef = [
            [ 'the ' ],
            [ 'doctor', 'knight', 'troll' ],
            [ ' drank ', ' stole ' ],
            [ 'beer', 'coffee', 'magic potion' ],
            [ 'a ', 'some ' ]
        ]
        bad_pattern_def_def = [
            [ 'the ' ],
            [ 'doctor', 'knight', 'troll' ],
            [ ' drank ', ' stole ' ],
            [ 'the ' ],
            [ 'beer', 'coffee', 'magic potion' ]
        ]
        bad_pattern_name_indef = [
            self.proper_names,
            [ ' drank ', ' stole ' ],
            [ 'beer', 'coffee', 'magic potion' ],
            [ 'a ' ]
        ]
        bad_pattern_name_def = [
            self.proper_names,
            [ ' drank ', ' stole ' ],
            [ 'the ' ],
            [ 'beer', 'coffee', 'magic potion' ]
        ]
        try:
            bad_indef_indef = [(self.translate(s), s) for s in itertools.product(*bad_pattern_indef_indef)]
            # filter out 'Some troll drank some beer' and similar
            bad_indef_indef = [(mar, eng) for mar, eng in bad_indef_indef if 'a ' in eng]
            bad_indef_indef = random.sample(bad_indef_indef, int(num_strings / 6 + 1))
            bad_indef_def = [(self.translate(s), s) for s in itertools.product(*bad_pattern_indef_def)]
            bad_indef_def = random.sample(bad_indef_def, int(num_strings / 6 + 1))
            bad_def_indef = [(self.translate(s), s) for s in itertools.product(*bad_pattern_def_indef)]
            bad_def_indef = random.sample(bad_def_indef, int(num_strings / 6 + 1))
            bad_def_def = [(self.translate(s), s) for s in itertools.product(*bad_pattern_def_def)]
            bad_def_def = random.sample(bad_def_def, int(num_strings / 6 + 1))
            bad_name_indef = [(self.translate(s), s) for s in itertools.product(*bad_pattern_name_indef)]
            bad_name_indef = random.sample(bad_name_indef, int(num_strings / 6 + 1))
            bad_name_def = [(self.translate(s), s) for s in itertools.product(*bad_pattern_name_def)]
            bad_name_def = random.sample(bad_name_def, int(num_strings / 6 + 1))
        except ValueError:
            return None
        # restore English word order
        bad_indef_indef = [(mar, (eng[1], eng[0], eng[2], eng[4], eng[3])) for mar, eng in bad_indef_indef]
        bad_indef_def = [(mar, (eng[1],) + (eng[0],) + eng[2:]) for mar, eng in bad_indef_def]
        bad_def_indef = [(mar, eng[0:3] + (eng[4],) + (eng[3],)) for mar, eng in bad_def_indef]
        bad_name_indef = [(mar, (eng[0], eng[1], eng[3], eng[2])) for mar, eng in bad_name_indef]
        ungrammatical_sentences = bad_indef_indef + bad_indef_def + bad_def_indef + bad_def_def + bad_name_indef + bad_name_def
        ungrammatical_sentences = random.sample(ungrammatical_sentences, num_strings)
        random.shuffle(ungrammatical_sentences)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class AccusativeMarkingAgreementGrammar(CustomGrammar):
    """A grammar fragment where nouns and their adjuncts agree in object marking."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
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

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_indef = [
            [ 'she', 'he' ] + self.proper_names,
            [ ' brought ', ' found ' ],
            [ 'a' ],
            [ ' basket', ' chair', ' horse' ],
            [ 'ACC' ]
        ]
        sentence_pattern_quant = [
            [ 'she', 'he' ] + self.proper_names,
            [ ' brought ', ' found ' ],
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

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
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
            [ 'she', 'a girl', 'two girls', self.proper_names[0] ],
            [ ' is ' ],
            [ 'eating', 'baking' ],
            [ 'FEM' ],
            [ '', ' pizza', ' a cake' ]
        ]
        sentence_pattern_masc = [
            [ 'he', 'a boy', 'two boys', self.proper_names[1] ],
            [ ' is ' ],
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
        sentences = [(mar, eng[0:1] + (' are ' if eng[0].startswith('two') else ' is ',) + eng[2:]) for mar, eng in sentences]
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

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
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
        sentence_pattern_name_short = [
            self.proper_names,
            [ ' speaks ', ' plays ' ],
            [ 'Dutch ', 'the piano ' ]
        ]
        sentence_pattern_name_long = [
            self.proper_names,
            [ ' speaks ', ' plays ' ],
            [ 'Dutch ', 'the piano ' ],
            [ ' speaks ', ' plays ' ],
            [ 'DE ' ],
            [ 'often', 'well' ]
        ]
        def object_makes_sense(sentence):
            # let the verbs select for the correct type of object, obviously
            if ((sentence[1] == ' plays '  and sentence[2] == 'the piano ') or
                (sentence[1] == ' speaks ' and sentence[2] == 'Dutch ') or
                (sentence[2] == 'plays '  and sentence[3] == 'the piano ') or
                (sentence[2] == 'speaks ' and sentence[3] == 'Dutch ')):
                try:
                    if (sentence[1] == sentence[3] or
                        sentence[2] == sentence[4]):
                        return True
                    else:
                        return False
                except IndexError:
                    return True
            else:
                return False
        try:
            sentences_short = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_short) if object_makes_sense(s)]
            sentences_short = random.sample(sentences_short, int(num_strings / 4 + 1))
            sentences_long = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_long) if object_makes_sense(s)]
            sentences_long = random.sample(sentences_long, int(num_strings / 4 + 1))
            sentences_name_short = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_name_short) if object_makes_sense(s)]
            sentences_name_short = random.sample(sentences_name_short, min(4, int(num_strings / 4 + 1)))
            sentences_name_long = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_name_long) if object_makes_sense(s)]
            sentences_name_long = random.sample(sentences_name_long, min(8, int(num_strings / 4 + 1)))
        except ValueError:
            return None
        # erase reduplication from the English translations
        sentences_long = [(mar, eng[0:4] + eng[6:]) for mar, eng in sentences_long]
        sentences_name_long = [(mar, eng[0:3] + eng[5:]) for mar, eng in sentences_name_long]
        sentences = sentences_short + sentences_long + sentences_name_short + sentences_name_long
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


class WackernagelWordOrderGrammar(CustomGrammar):
    """A grammar fragment where a pronoun is always in the 2nd slot of the sentence."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) and ('m' in s or 'n' in s) for s in self.tokens)
        assert any(monosyll(s) and ('m' not in s) for s in self.tokens)
        me_clitic = [s for s in self.tokens if monosyll(s) and ('m' in s or 'n' in s)][0]
        him_clitic = [s for s in self.tokens if monosyll(s) and ('m' not in s and 'n' not in s)][0]
        remaining_tokens = list(set(self.tokens) - set({me_clitic, him_clitic}))
        while not monosyll(remaining_tokens[4]) or not monosyll(remaining_tokens[5]):
            random.shuffle(remaining_tokens)
        self.lexicon = {
            'you'          : remaining_tokens[0],
            'they'         : remaining_tokens[1],
            'found'        : remaining_tokens[2],
            'left'         : remaining_tokens[3],
            'me'           : me_clitic,
            'him'          : him_clitic,
            'a'            : remaining_tokens[4],
            'the'          : remaining_tokens[5],
            'password'     : remaining_tokens[6],
            'room'         : remaining_tokens[7],
            'empty'        : remaining_tokens[8],
            'immediately'  : remaining_tokens[9]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_nom_object = [
            [ 'you', 'they' ] + self.proper_names,
            [ ' found ', ' left ' ],
            [ ' a ', ' the ' ],
            [ 'password ', 'room ' ],
            [ '', 'empty', 'immediately' ]
        ]
        sentence_pattern_pro_object = [
            [ 'you', 'they' ] + self.proper_names,
            [ ' me ', ' him ' ],
            [ ' found ', ' left ' ]
        ]
        sentence_pattern_ditransitive = [
            [ 'you', 'they' ] + self.proper_names,
            [ ' me ', ' him ' ],
            [ ' found ', ' left ' ],
            [ ' a ', ' the ' ],
            [ 'password ', 'room ' ],
            [ '', 'immediately' ]
        ]
        try:
            sentences_nom_object = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_nom_object)]
            sentences_nom_object = random.sample(sentences_nom_object, int(num_strings / 3 + 0.67))
            sentences_pro_object = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_pro_object)]
            sentences_pro_object = random.sample(sentences_pro_object, int(num_strings / 3 + 0.67))
            sentences_dtr_object = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_ditransitive)]
            sentences_dtr_object = random.sample(sentences_dtr_object, int(num_strings / 3 + 0.67))
        except ValueError:
            return None
        # restore actual English word order
        sentences_pro_object = [(mar, eng[0:1] + eng[2:3] + eng[1:2]) for mar, eng in sentences_pro_object]
        sentences_dtr_object = [(mar, eng[0:1] + eng[2:3] + eng[1:2] + eng[3:]) for mar, eng in sentences_dtr_object]
        sentences = sentences_nom_object + sentences_pro_object + sentences_dtr_object
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
            if form[1] in ['found ', 'left ']:
                # no pro object, flip verb and object
                form = form[0:1] + form[2:4] + form[1:2] + form[4:]
            else:
                # pro object, flip object and verb
                form = form[0:1] + form[2:3] + form[1:2] + form[3:]
            sentence = (form, meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class LeadingCopulaGrammar(CustomGrammar):
    """A grammar fragment where all sentences start with a (vacuous) verb 'to be' and feature
    a (similarly vacuous) particle in front of the main predicate."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[7]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'is'         : self.tokens[0],
            'are'        : self.tokens[1],
            'the baker'  : self.tokens[2],
            'the pirate' : self.tokens[3],
            'we'         : self.tokens[4],
            'they'       : self.tokens[5],
            'also'       : self.tokens[6],
            'YN'         : self.tokens[7],
            'like'       : self.tokens[8],
            'sell'       : self.tokens[9],
            'bubble tea' : self.tokens[10],
            'pancakes'   : self.tokens[11]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_sg_subject = [
            [ 'is ' ],
            [ 'the baker', 'the pirate' ] + self.proper_names,
            [ '', ' also ' ],
            [ ' YN ' ],
            [ ' like', ' sell' ],
            [ ' bubble tea', ' pancakes' ]
        ]
        sentence_pattern_pl_subject = [
            [ 'are ' ],
            [ 'we', 'they' ],
            [ '', ' also ' ],
            [ ' YN ' ],
            [ ' like', ' sell' ],
            [ ' bubble tea', ' pancakes' ]
        ]
        try:
            sentences_sg_subject = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_sg_subject)]
            sentences_sg_subject = random.sample(sentences_sg_subject, int(num_strings / 2 + 0.5))
            sentences_pl_subject = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_pl_subject)]
            sentences_pl_subject = random.sample(sentences_pl_subject, int(num_strings / 2 + 0.5))
        except ValueError:
            return None
        # Martian is fine, English needs number agreement
        sentences_sg_subject = [(mar, eng[0:-2] + (eng[-2]+'s',) + eng[-1:]) for mar, eng in sentences_sg_subject]
        sentences = sentences_sg_subject + sentences_pl_subject
        # restore actual English word order
        sentences = [(mar, eng[1:3] + eng[4:]) for mar, eng in sentences]
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
                    # leave out the particle YN
                    form = form[0:3] + form[4:]
                    done = True
                if random.choice([True, False]):
                    # leave out the verb to be
                    form = form[1:]
                    done = True
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class PresentParticipleGrammar(CustomGrammar):
    """A grammar fragment where adjectival present participles are morphologically marked,
    as opposed to present progressive finite verb forms, which are unmarked."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[2]) or monosyll(self.tokens[6]) or monosyll(self.tokens[7]) or not monosyll(self.tokens[8]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'the'      : '',
            'postman'  : self.tokens[0],
            'tourists' : self.tokens[1],
            'is'       : self.tokens[2],
            'are'      : self.tokens[2], # make Martian copula invariant
            'still'    : self.tokens[3],
            'bored'    : self.tokens[4],
            'happy'    : self.tokens[5],
            'talking'  : self.tokens[6],
            'waiting'  : self.tokens[7],
            'APRT'     : self.tokens[8]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_no_prt = [
            [ 'the ' ],
            [ '', '', 'bored', 'happy' ],  # sic, two empty strings intentional
            [ ' postman ', ' tourists ' ],
            [ 'is ', 'are ' ],
            [ '', 'still ' ],
            [ 'bored', 'happy', 'talking', 'waiting' ]
        ]
        sentence_pattern_prt = [
            [ 'the ' ],
            [ 'talking', 'waiting' ],
            [ 'APRT' ],
            [ ' postman ', ' tourists ' ],
            [ 'is ', 'are ' ],
            [ '', 'still ' ],
            [ 'bored', 'happy', 'talking', 'waiting' ]
        ]
        sentence_pattern_name_no_prt = [
            self.proper_names,
            [ ' is ' ],
            [ '', 'still ' ],
            [ 'bored', 'happy', 'talking', 'waiting' ]
        ]
        def num_agrees(sentence):
            # check if the copula is conjugated right
            if ((sentence[-4] == ' postman '  and sentence[-3] == 'is ') or
                (sentence[-4] == ' tourists ' and sentence[-3] == 'are ')):
                return True
            return False
        try:
            while True:
                sentences_no_prt = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_no_prt) if num_agrees(s)]
                sentences_no_prt = random.sample(sentences_no_prt, int(num_strings / 3 + 1))
                # we might have got the same sentence twice on account of the double empty string in slot #2
                if len(sentences_no_prt) == len(set(sentences_no_prt)):
                    break
            sentences_prt = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_prt) if num_agrees(s)]
            sentences_prt = random.sample(sentences_prt, int(num_strings / 3 + 1))
            sentences_name_no_prt = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_name_no_prt)]
            sentences_name_no_prt = random.sample(sentences_name_no_prt, int(num_strings / 3 + 1))
        except ValueError:
            return None
        # erase special participle marker from English translations
        sentences_prt = [(mar, eng[0:2] + eng[3:]) for mar, eng in sentences_prt]
        sentences = sentences_no_prt + sentences_prt + sentences_name_no_prt
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
            if meaning[1].endswith('ing'):
                # has present participle
                done = False
                form, meaning = sentence
                while not done:
                    if random.choice([True, False]):
                        # add faulty APRT marker to verb
                        form = form + (self.translate('APRT'),)
                        done = True
                    if random.choice([True, False]):
                        # remove APRT marker from participle
                        form = form[0:2] + form[3:]
                        done = True
            else:
                # no present participle
                if meaning[-1].endswith('ing'):
                    # add faulty APRT marker to verb
                    form = form + (self.translate('APRT'),)
                elif len(meaning[1]):
                    # add nonsense APRT marker to plain adjective
                    form = form[0:2] + (self.translate('APRT'),) + form[2:]
                else:
                    # sentence too simple, try again
                    continue
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class EvidentialGrammar(CustomGrammar):
    """A grammar fragment that distinguishes three kinds of evidentiality, all overtly marked:
    direct knowledge, hearsay, and circumstantial inference."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[0]) or monosyll(self.tokens[10]) or monosyll(self.tokens[11]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'the'       : self.tokens[0],
            'dwarves'   : self.tokens[1],
            'monkeys'   : self.tokens[2],
            'is'        : self.tokens[3],
            'are'       : self.tokens[3],
            'has'       : self.tokens[4],
            'have'      : self.tokens[4],
            'building'  : self.tokens[5], # tense/aspect morphologically unmarked
            'built'     : self.tokens[5], # tense/aspect morphologically unmarked
            'occupying' : self.tokens[6], # tense/aspect morphologically unmarked
            'occupied'  : self.tokens[6], # tense/aspect morphologically unmarked
            'DIR'       : self.tokens[7],
            'HEAR'      : self.tokens[8],
            'INF'       : self.tokens[9],
            'a castle'  : self.tokens[10],
            'a tavern'  : self.tokens[11]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern = [
            [ 'the ' ],
            [ 'dwarves ', 'monkeys ' ],
            [ ' are', ' have' ],
            [ ' building', ' built', ' occupying', ' occupied' ],
            [ 'DIR', 'HEAR', 'INF' ],
            [ ' a castle', ' a tavern' ]
        ]
        sentence_pattern_name = [
            self.proper_names,
            [ ' is', ' has' ],
            [ ' building', ' built', ' occupying', ' occupied' ],
            [ 'DIR', 'HEAR', 'INF' ],
            [ ' a castle', ' a tavern' ]
        ]
        def aux_correct(sentence):
            # check if the auxiliary matches the intended tense
            if sentence[-4] in [' is', ' are']:
                if sentence[-3] in [' building', ' occupying']:
                    return True
            else:
                if sentence[-3] in [' built', ' occupied']:
                    return True
            return False
        try:
            sentences_vanilla = [(self.translate(s), s) for s in itertools.product(*sentence_pattern) if aux_correct(s)]
            sentences_vanilla = random.sample(sentences_vanilla, int(num_strings / 2 + 0.5))
            sentences_name = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_name) if aux_correct(s)]
            sentences_name = random.sample(sentences_name, int(num_strings / 2 + 0.5))
        except ValueError:
            return None
        sentences = sentences_vanilla + sentences_name
        # remove grammatical evidentiality marker, add a matrix phrase in English
        def eng_phrase(eng):
            if eng[-2] == 'DIR':
                return 'I saw that '
            if eng[-2] == 'HEAR':
                return 'I heard that '
            if eng[-2] == 'INF':
                return 'It looks like '
            assert False
        sentences = [(mar, (eng_phrase(eng),) + eng[0:-2] + eng[-1:]) for mar, eng in sentences]
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
            # remove evidentiality marker from lexical (main) verb
            evid = form[4]
            form = form[0:4] + form[5:]
            if random.choice([True, False]):
                # drop it on the auxiliary verb for kicks
                form = form[0:2] + (form[2] + evid,) + form[3:]
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class EchoMorphologyGrammar(CustomGrammar):
    """A grammar fragment where each word's first vowel is redoubled after a common consonant."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        self.consonant = random.choice(['g', 'm', 't'])
        def redouble_first(string):
            # reduplicate first syllable, kinda
            return re.sub(r"\b([^aeiouy]*)([aeiou]+|y+)", r"\1\2" + self.consonant + r"\2", string)
        self.unechoed_lexicon = {
            'all'         : self.tokens[0],
            'dogs'        : self.tokens[1],
            'ninjas'      : self.tokens[2],
            'robots'      : self.tokens[3],
            'can'         : self.tokens[4],
            'should'      : self.tokens[5],
            'like to'     : self.tokens[6],
            'likes to'    : self.tokens[6],
            'swim'        : self.tokens[7],
            'help others' : self.tokens[8] + ' ' + self.tokens[9]
        }
        self.lexicon = {eng : redouble_first(mar) for eng, mar in self.unechoed_lexicon.items()}

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern = [
            [ '', 'all ' ],
            [ 'dogs ', 'ninjas ', 'robots ' ],
            [ 'can ', 'should ', 'like to ' ],
            [ 'swim', 'help others' ]
        ]
        sentence_pattern_name = [
            self.proper_names,
            [ ' can ', ' should ', ' likes to ' ],
            [ 'swim', 'help others' ]
        ]
        try:
            sentences_vanilla = [(self.translate(s), s) for s in itertools.product(*sentence_pattern)]
            sentences_vanilla = random.sample(sentences_vanilla, int(num_strings / 2 + 0.5))
            sentences_name = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_name)]
            sentences_name = random.sample(sentences_name, int(num_strings / 2 + 0.5))
        except ValueError:
            return None
        sentences = sentences_vanilla + sentences_name
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
            done = False
            while not done:
                # revert a few words to their "unechoed" forms
                for i in range(len(form)):
                    if form[i] and random.choice([True, False, False]):
                        altered_word = self.translate([meaning[i]], lexicon=self.unechoed_lexicon)[0]
                        if random.choice([True, False]):
                            def redouble_first(string):
                                # reduplicate first syllable, kinda
                                consonants = ['g', 'm', 't', 'g']
                                consonant = consonants[consonants.index(self.consonant)+1]
                                return re.sub(r"\b([^aeiouy]*)([aeiou]+|y+)", r"\1\2" + consonant + r"\2", string)
                            altered_word = redouble_first(altered_word)
                        form = form[0:i] + (altered_word,) + form[i+1:]
                        done = True
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class RhymingGrammar(CustomGrammar):
    """A grammar fragment where the two clauses of a conditional construction need to rhyme."""

    def __init__(self, tokens, proper_names, rhymes):
        super().__init__(tokens, proper_names, rhymes)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[1]) or not monosyll(self.tokens[3]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'if'       : self.tokens[0],
            'you'      : self.tokens[1],
            'feed'     : self.tokens[2],
            'your'     : self.tokens[1],
            'my'       : self.tokens[3],
            'hamster'  : self.tokens[4],
            'parrot'   : self.tokens[5],
            'seeds'    : self.rhymes[0][0],
            'snacks'   : self.rhymes[1][0],
            'it'       : '',
            'will'     : self.tokens[6],
            'be happy' : self.rhymes[0][1],
            'get fat'  : self.rhymes[1][1],
            'we'       : self.tokens[7],
            'leave'    : self.tokens[8],
            'early'    : self.rhymes[2][0],
            'now'      : self.rhymes[3][0],
            'arrive on time'   : self.tokens[9] + ' ' + self.rhymes[2][1],
            'beat the traffic' : self.tokens[10] + ' ' + self.rhymes[3][1]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_feed_1 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            [ 'your ', 'my ' ],
            [ 'hamster ', 'parrot ' ],
            [ 'seeds ' ],  # this word...
            [ 'it ' ],
            [ 'will ' ],
            [ 'be happy' ] # ...will rhyme with this
        ]
        sentence_pattern_feed_2 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            [ 'your ', 'my ' ],
            [ 'hamster ', 'parrot ' ],
            [ 'snacks ' ], # this word...
            [ 'it ' ],
            [ 'will ' ],
            [ 'get fat' ]  # ...will rhyme with this
        ]
        sentence_pattern_feed_name_1 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            self.proper_names,
            [ ' seeds ' ],  # this word...
            [ 'it ' ],
            [ 'will ' ],
            [ 'be happy' ] # ...will rhyme with this
        ]
        sentence_pattern_feed_name_2 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            self.proper_names,
            [ ' snacks ' ], # this word...
            [ 'it ' ],
            [ 'will ' ],
            [ 'get fat' ]  # ...will rhyme with this
        ]
        sentence_pattern_leave_1 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'leave ' ],
            [ 'early ' ],        # this word...
            [ 'you ', 'we ' ],
            [ 'will ' ],
            [ 'arrive on time' ] # ...will rhyme with this
        ]
        sentence_pattern_leave_2 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'leave ' ],
            [ 'now ' ],            # this word...
            [ 'you ', 'we ' ],
            [ 'will ' ],
            [ 'beat the traffic' ] # ...will rhyme with this
        ]
        try:
            sentences_leave_1 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_leave_1)]
            sentences_leave_2 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_leave_2)]
            num_to_go = num_strings - len(sentences_leave_1) - len(sentences_leave_2)
            sentences_feed_1 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_feed_1)]
            sentences_feed_1 = random.sample(sentences_feed_1, int(num_to_go / 4 + 0.25))
            sentences_feed_2 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_feed_2)]
            sentences_feed_2 = random.sample(sentences_feed_2, int(num_to_go / 4 + 0.25))
            sentences_feed_name_1 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_feed_name_1)]
            sentences_feed_name_1 = random.sample(sentences_feed_name_1, int(num_to_go / 4 + 0.25))
            sentences_feed_name_2 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_feed_name_2)]
            sentences_feed_name_2 = random.sample(sentences_feed_name_2, int(num_to_go / 4 + 0.25))
        except ValueError:
            return None
        # fix personal pronouns in English
        sentences_feed_name_1 = [(mar, eng[0:5] + ('she ' if self.proper_names[0] == eng[3] else 'he ',) + eng[6:]) for mar, eng in sentences_feed_name_1]
        sentences_feed_name_2 = [(mar, eng[0:5] + ('she ' if self.proper_names[0] == eng[3] else 'he ',) + eng[6:]) for mar, eng in sentences_feed_name_2]
        sentences = sentences_feed_1 + sentences_feed_2 + sentences_feed_name_1 + sentences_feed_name_2 + sentences_leave_1 + sentences_leave_2
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        nonrhyming_pattern_feed_1 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            [ 'your ', 'my ' ],
            [ 'hamster ', 'parrot ' ],
            [ 'seeds ' ],
            [ 'it ' ],
            [ 'will ' ],
            [ 'get fat' ]
        ]
        nonrhyming_pattern_feed_2 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            [ 'your ', 'my ' ],
            [ 'hamster ', 'parrot ' ],
            [ 'snacks ' ],
            [ 'it ' ],
            [ 'will ' ],
            [ 'be happy' ]
        ]
        nonrhyming_pattern_feed_name_1 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            self.proper_names,
            [ ' seeds ' ],
            [ 'it ' ],
            [ 'will ' ],
            [ 'get fat' ]
        ]
        nonrhyming_pattern_feed_name_2 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'feed ' ],
            self.proper_names,
            [ ' snacks ' ],
            [ 'it ' ],
            [ 'will ' ],
            [ 'be happy' ]
        ]
        nonrhyming_pattern_leave_1 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'leave ' ],
            [ 'early ' ],
            [ 'you ', 'we ' ],
            [ 'will ' ],
            [ 'beat the traffic' ]
        ]
        nonrhyming_pattern_leave_2 = [
            [ 'if ' ],
            [ 'you ', 'we ' ],
            [ 'leave ' ],
            [ 'now ' ],
            [ 'you ', 'we ' ],
            [ 'will ' ],
            [ 'arrive on time' ]
        ]
        nonrhyming_feed_1 = [(self.translate(s), s) for s in itertools.product(*nonrhyming_pattern_feed_1)]
        nonrhyming_feed_2 = [(self.translate(s), s) for s in itertools.product(*nonrhyming_pattern_feed_2)]
        nonrhyming_feed_name_1 = [(self.translate(s), s) for s in itertools.product(*nonrhyming_pattern_feed_name_1)]
        nonrhyming_feed_name_2 = [(self.translate(s), s) for s in itertools.product(*nonrhyming_pattern_feed_name_2)]
        # fix personal pronouns in English
        nonrhyming_feed_name_1 = [(mar, eng[0:5] + ('she ' if self.proper_names[0] == eng[3] else 'he ',) + eng[6:]) for mar, eng in nonrhyming_feed_name_1]
        nonrhyming_feed_name_2 = [(mar, eng[0:5] + ('she ' if self.proper_names[0] == eng[3] else 'he ',) + eng[6:]) for mar, eng in nonrhyming_feed_name_2]
        nonrhyming_leave_1 = [(self.translate(s), s) for s in itertools.product(*nonrhyming_pattern_leave_1)]
        nonrhyming_leave_2 = [(self.translate(s), s) for s in itertools.product(*nonrhyming_pattern_leave_2)]
        nonrhyming = nonrhyming_feed_1 + nonrhyming_feed_2 + nonrhyming_feed_name_1 + nonrhyming_feed_name_2 + nonrhyming_leave_1 + nonrhyming_leave_2
        ungrammatical_sentences = set(random.sample(nonrhyming, k=num_strings))
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            form, meaning = sentence
            index = random.choice([-4, -1])
            while True:
                bad_rhyme = random.choice(self.rhymes)
                if form[index] not in bad_rhyme:
                    bad_rhyme = random.choice(bad_rhyme)
                    break
            form = form[0:index] + (bad_rhyme,) + form[index+1:]
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class PalindromeDemonstrativeGrammar(CustomGrammar):
    """A grammar fragment where the form of the word 'that' is always its noun reversed."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        def palindrome(string):
            naked_string = string.strip()
            return naked_string == naked_string[::-1]
        while any(map(monosyll, (self.tokens[2], self.tokens[3], self.tokens[4]))) or all(map(palindrome, (self.tokens[2], self.tokens[3], self.tokens[4]))):
            random.shuffle(self.tokens)
        self.lexicon = {
            'that'      : 'THAT',
            'the left'  : self.tokens[0],
            'the right' : self.tokens[1],
            'bird'      : self.tokens[2],
            'image'     : self.tokens[3],
            'totem'     : self.tokens[4],
            'colors'    : self.tokens[5],
            'nice'      : self.tokens[6],
            'strange'   : self.tokens[7],
            'symbolizes': self.tokens[8],
            'freedom'   : self.tokens[9],
            'luck'      : self.tokens[10]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_colors = [
            [ ' that ', 'the left ', 'the right ' ],
            [ ' bird ', ' image ', ' totem ' ],
            [ 'colors ' ],
            [ 'nice ', 'strange ' ]
        ]
        sentence_pattern_symbol = [
            [ ' that ', 'the left ', 'the right ' ],
            [ ' bird ', ' image ', ' totem ' ],
            [ 'symbolizes ' ],
            [ 'freedom', 'luck' ]
        ]
        sentence_pattern_colors_name = [
            [ ' bird ', ' image ', ' totem ' ],
            [ name + ('\'' if name[-1] == 's' else '\'s') for name in self.proper_names ],
            [ ' colors ' ],
            [ 'nice ', 'strange ' ]
        ]
        sentence_pattern_symbol_name = [
            [ ' bird ', ' image ', ' totem ' ],
            [ name + ('\'' if name[-1] == 's' else '\'s') for name in self.proper_names ],
            [ ' symbolizes ' ],
            [ 'freedom', 'luck' ]
        ]
        try:
            sentences_colors = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_colors)]
            sentences_colors = random.sample(sentences_colors, int(num_strings / 2 + 0.5))
            sentences_symbol = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_symbol)]
            sentences_symbol = random.sample(sentences_symbol, int(num_strings / 2 + 0.5))
            sentences_colors_name = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_colors_name)]
            sentences_colors_name = random.sample(sentences_colors_name, 1)
            sentences_symbol_name = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_symbol_name)]
            sentences_symbol_name = random.sample(sentences_symbol_name, 1)
        except ValueError:
            return None
        # correct English word order
        sentences_colors = [(mar, eng[0:2] + ('has ',) + eng[3:4] + eng[2:3]) for mar, eng in sentences_colors]
        sentences_colors_name = [(mar, eng[1:2] + eng[0:1] + ('has ',) + eng[3:4] + eng[2:3]) for mar, eng in sentences_colors_name]
        sentences_symbol_name = [(mar, eng[1:2] + eng[0:1] + eng[2:]) for mar, eng in sentences_symbol_name]
        sentences = sentences_colors + sentences_symbol + sentences_colors_name + sentences_symbol_name
        # render Martian demonstrative
        def rev(string):
            rev_string = string[::-1]
            rev_string = re.sub('hc', 'ch', rev_string)
            rev_string = re.sub('hs', 'sh', rev_string)
            rev_string = re.sub('hk', 'kh', rev_string)
            return rev_string
        sentences = [((rev(mar[1])+' ' if 'THAT' in mar[0] else mar[0],) + mar[1:], eng) for mar, eng in sentences]
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        def palindrome(string):
            naked_string = string.strip()
            return naked_string == naked_string[::-1]
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            form, meaning = sentence
            if form[1] in self.proper_names:
                continue
            if meaning[0] == ' that ':
                # make sure the noun head isn't the reverse of itself
                if not palindrome(form[1]) and random.choice([True, False]):
                    # use noun phrase head without reversing it
                    form = (form[1]+' ',) + form[1:]
                else:
                    # use last remaining token, not seen in training data
                    form = (self.tokens[11]+' ',) + form[1:]
            elif not palindrome(form[1]) and not form[1] in self.proper_names:
                # reduplicate noun phrase head without reversing it
                form = (form[1]+' ',) + form[1:]
            else:
                continue
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class PalindromePastGrammar(CustomGrammar):
    """A grammar fragment where the past tense is indicated by the whole sentence
    being the same read forwards and backwards."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        while (monosyll(self.tokens[0]) or monosyll(self.tokens[1]) or monosyll(self.tokens[2])
               or not monosyll(self.tokens[6]) or not monosyll(self.tokens[7])):
            random.shuffle(self.tokens)
        self.lexicon = {
            'the mayor'          : self.tokens[0],
            'the fortune-teller' : self.tokens[1],
            'the sheriff'        : self.tokens[2],
            'arrive'             : self.tokens[3],
            'arrived'            : self.tokens[3],
            'come'               : self.tokens[4],
            'came'               : self.tokens[4],
            'FUT'                : self.tokens[5],
            'alone'              : self.tokens[6] + self.rev(self.tokens[6]),
            'as well'            : self.tokens[7] + self.rev(self.tokens[7]),
            'from'               : self.rev(self.tokens[4]),
            'to'                 : self.rev(self.tokens[3]),
            'the north'          : self.rev(self.tokens[2]),
            'the south'          : self.rev(self.tokens[1]),
            'the town square'    : self.rev(self.tokens[0]),
            'the shop'           : self.rev(self.proper_names[0]).lower()
        }

    def rev(_self, string):
        """Return the same string backwards."""
        rev_string = string[::-1]
        rev_string = re.sub('hc', 'ch', rev_string)
        rev_string = re.sub('hs', 'sh', rev_string)
        rev_string = re.sub('hk', 'kh', rev_string)
        return rev_string

    def produce_grammatical(self, num_strings=1, polish=True):
        subject_with_place = [
            (self.proper_names[0] + ' ', 'the shop'),
            ('the mayor ', 'the town square'),
            ('the sheriff ', 'the north'),
            ('the fortune-teller ', 'the south')
        ]
        verb_with_direction = [
            ('arrived ', ' to '),
            ('came ', ' from ')
        ]
        adverb = [ '', '', ' alone', ' as well' ]
        try:
            while True:
                sentences_past = [(sp[0], vd[0], a, vd[1], sp[1]) for sp, vd, a in itertools.product(subject_with_place, verb_with_direction, adverb)]
                sentences_past = [(self.translate(s), s) for s in sentences_past]
                sentences_past = random.sample(sentences_past, int(num_strings / 2 + 0.5))
                # we might have got the same sentence twice on account of the double empty string
                if len(sentences_past) == len(set(sentences_past)):
                    break
            sentence_pattern_fut = [
                [ self.proper_names[0] + ' ', 'the mayor ', 'the sheriff ', 'the fortune-teller ' ],
                [ 'arrive', 'come' ],
                [ 'FUT' ],
                [ '', '', ' alone ', ' as well ' ],
                [ ' from ', ' to ' ],
                [ 'the north', 'the south', 'the town square', 'the shop' ]
            ]
            while True:
                sentences_fut = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_fut)]
                sentences_fut = random.sample(sentences_fut, int(num_strings / 2 + 0.5))
                # we might have got the same sentence twice on account of the double empty string
                if len(sentences_fut) == len(set(sentences_fut)):
                    break
        except ValueError:
            return None
        # Martian is fine, rearrange English translations
        sentences_past = [(mar, eng[0:2] + eng[3:] + (eng[2],)) for mar, eng in sentences_past]
        sentences_fut = [(mar, eng[0:1] + ('will ',) + eng[1:2] + eng[4:] + (eng[3],)) for mar, eng in sentences_fut]
        sentences = sentences_past + sentences_fut
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        bad_pattern_past = [
            [ self.proper_names[0] + ' ', 'the mayor ', 'the sheriff ', 'the fortune-teller ' ],
            [ 'arrived', 'came' ],
            [ '', '', ' alone ', ' as well ' ],
            [ ' from ', ' to ' ],
            [ 'the north', 'the south', 'the town square' ]
        ]
        def check_bad(sentence):
            subject_with_place = [
                (self.proper_names[0] + ' ', 'the shop'),
                ('the mayor ', 'the town square'),
                ('the sheriff ', 'the north'),
                ('the fortune-teller ', 'the south')
            ]
            verb_with_direction = [
                ('arrived', ' to '),
                ('came', ' from ')
            ]
            if (sentence[0], sentence[4]) in subject_with_place and (sentence[1], sentence[3]) in verb_with_direction:
                return False
            return True
        bad_past_sentences = [(self.translate(s), s) for s in itertools.product(*bad_pattern_past) if check_bad(s)]
        # Martian is fine, rearrange English translations
        bad_past_sentences = [(mar, eng[0:2] + eng[3:] + (eng[2],)) for mar, eng in bad_past_sentences]
        ungrammatical_sentences = set(random.sample(bad_past_sentences, k=int((num_strings+1)/2)))
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            form, meaning = sentence
            if self.translate('FUT') not in form:
                # try again
                continue
            assert form[2] == self.translate('FUT')
            # put FUT morpheme on subject instead of the verb
            form = (form[0][:-1],) + (form[2]+' ',) + form[1:2] + form[3:]
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class RecursiveGrammar(CustomGrammar):
    """A grammar fragment where possession needs to be overtly marked, and btw
    the possessive structure can be self-nested arbitrarily deep."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        while not monosyll(self.tokens[2]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'we'         : self.tokens[0],
            'they'       : self.tokens[1],
            'the'        : '',
            'with'       : '',
            'with the'   : '',
            '\''         : self.tokens[2],  # awkward special English genitive ending for a noun ending in s
            '\'s'        : self.tokens[2],
            self.proper_names[0]+'\'s' : self.proper_names[0] + self.tokens[2],
            self.proper_names[1]+'\'s' : self.proper_names[1] + self.tokens[2],
            'enemy'      : self.tokens[3],
            'brother'    : self.tokens[4],
            'dog'        : self.tokens[5],
            'friend'     : self.tokens[6],
            'student'    : self.tokens[7],
            'teacher'    : self.tokens[8],
            'is brewing' : self.tokens[9],
            'are brewing': self.tokens[9],
            'is having'  : self.tokens[10],
            'are having' : self.tokens[10],
            'coffee'     : self.tokens[11],
            'with us'    : self.tokens[0],
            'with them'  : self.tokens[1]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        recursables = [ 'enemy', 'brother', 'dog', 'friend', 'student', 'teacher' ]
        sentence_pattern_sg_subject = [
            [ 'the ' ] + self.proper_names,
            [ '' ] + recursables,
            [ ' coffee ' ],
            [ ' is brewing', ' is having' ],
            [ ' with us', ' with them' ]
        ]
        sentence_pattern_pl_subject = [
            [ 'we ', 'they ' ],
            [ ' coffee ' ],
            [ ' are brewing', ' are having' ],
            [ ' with '],
            [ 'the ' ] + self.proper_names,
            [ '' ] + recursables
        ]
        def expand(sentence):
            # expand the recursive structure
            recursables_remaining = set(recursables)
            if sentence[0] in ['the '] + self.proper_names:
                if sentence[1]:
                    recursables_remaining.remove(sentence[1])
            else:
                if sentence[5]:
                    recursables_remaining.remove(sentence[5])
            if sentence[0] in self.proper_names and sentence[1] not in ['', '\'s ']:
                sentence = sentence[0:1] + ('\'s ',) + sentence[1:]
            if sentence[4] in self.proper_names and sentence[5] not in ['', '\'s ']:
                sentence = sentence[0:5] + ('\'s ',) + sentence[5:]
            while random.choice([True, True, True, False]):
                if not recursables_remaining:
                    break
                new_noun = random.choice(list(recursables_remaining))
                if sentence[0] in self.proper_names:
                    # assert sentence[1] in recursables
                    sentence = sentence[0:1] + ('\'s ', new_noun) + sentence[1:]
                elif sentence[0] == 'the ':
                    sentence = sentence[0:2] + ('\'s ', new_noun) + sentence[2:]
                else:
                    # assert sentence[6] in recursables
                    sentence = sentence + ('\'s ', new_noun)
                recursables_remaining.remove(new_noun)
            # fix possessive endings after an s
            sentence = tuple('\' ' if sentence[i] == '\'s ' and sentence[i-1].endswith('s') else sentence[i] for i in range(len(sentence)))
            return sentence
        sentences_sg_subject_basic = [s for s in itertools.product(*sentence_pattern_sg_subject) if s[0] != 'the ' or s[1]]
        sentences_pl_subject_basic = [s for s in itertools.product(*sentence_pattern_pl_subject) if s[4] != 'the ' or s[5]]
        sentences_sg_subject = set()
        sentences_pl_subject = set()
        sentences = set()
        while len(sentences) < num_strings:
            more_sentences_sg_subject = [expand(s) for s in sentences_sg_subject_basic]
            sentences_sg_subject.update({(self.translate(s), s) for s in more_sentences_sg_subject})
            # Martian is fine, reorder English translations
            sentences_sg_subject = {(mar, (eng[0:-3] + (eng[-2],) + (eng[-3],) + eng[-1:])) for mar, eng in sentences_sg_subject}
            more_sentences_pl_subject = [expand(s) for s in sentences_pl_subject_basic]
            sentences_pl_subject.update({(self.translate(s), s) for s in more_sentences_pl_subject})
            # Martian is fine, reorder English translations
            sentences_pl_subject = {(mar, (eng[0:1] + (eng[2],) + (eng[1],) + eng[3:])) for mar, eng in sentences_pl_subject}
            sentences = sentences_sg_subject.union(sentences_pl_subject)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        sentences = list(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        ungrammatical_sentences = set()
        while len(ungrammatical_sentences) < num_strings:
            sentence = self.produce_grammatical(1, polish=False)[0]
            form, meaning = sentence
            done = False
            while not done:
                # remove at least one of the possessive morphemes
                possessives = list(filter(lambda i: self.translate('\'s') == form[i].strip(), range(len(form))))
                leave_possessive = [random.choice([True, True, True, False]) if i in possessives else True for i in range(len(form))]
                done = not all(leave_possessive)
                form = tuple([form[i] if leave_possessive[i] else ' ' for i in range(len(form))])
                if random.choice([True, False, False, False]):
                    # attach unnecessary possessive morpheme to the actual head
                    recursables_in_martian = [self.translate(s) for s in ['enemy', 'brother', 'dog', 'friend', 'student', 'teacher']]
                    for i in range(len(form)-1, -1, -1):
                        if form[i] in recursables_in_martian + self.proper_names:
                            break
                    assert form[i] in recursables_in_martian + self.proper_names
                    form = form[0:i+1] + (self.translate('\'s'),) + form[i+1:] # off by one?
                    done = True
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class PredicativeEndingGrammar(CustomGrammar):
    """A grammar fragment where adjectives used as predicates are overtly marked, taking the same ending
    as the subject, but adjectives used as an adjunct with a noun are unmarked."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[0]) or all(monosyll(t) for t in self.tokens[2:6]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'the'   : self.tokens[0],
            'dress' : self.tokens[1],
            'skirt' : self.tokens[2],
            'bike'  : self.tokens[3],
            'car'   : self.tokens[4],
            'green' : self.tokens[5],
            'red'   : self.tokens[6],
            'nice'  : self.tokens[7],
            'long'  : self.tokens[8],
            'tall'  : self.tokens[8],
            'short' : self.tokens[9],
            'fast'  : self.tokens[10],
            'slow'  : self.tokens[11],
            'is'    : '',
            'PRED'  : ''
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_clothes = [
            [ 'the' ],
            [ '', '', ' nice', ' long' ],
            [ '', '', ' green', ' red' ],
            [ ' dress ', ' skirt ' ],
            [ 'is ' ],
            [ 'green', 'red', 'nice', 'long' ],
            [ 'PRED' ]
        ]
        sentence_pattern_vehicles = [
            [ 'the ' ],
            [ '', '', ' fast', ' slow', ' green', ' red' ],
            [ ' bike ', ' car ' ],
            [ 'is ' ],
            [ 'nice', 'long', 'fast', 'slow' ],
            [ 'PRED' ]
        ]
        sentence_pattern_names = [
            self.proper_names,
            [ ' is ' ],
            [ 'nice', 'tall', 'fast', 'slow' ],
            [ 'PRED' ]
        ]
        try:
            sentences_clothes = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_clothes)]
            sentences_clothes = list(set(sentences_clothes))
            sentences_clothes = random.sample(sentences_clothes, int(num_strings / 3 + 1))
            sentences_vehicles = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_vehicles)]
            sentences_vehicles = list(set(sentences_vehicles))
            sentences_vehicles = random.sample(sentences_vehicles, int(num_strings / 3 + 1))
            sentences_names = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_names)]
            sentences_names = list(set(sentences_names))
            sentences_names = random.sample(sentences_names, int(num_strings / 3))
        except ValueError:
            return None
        sentences = sentences_clothes + sentences_vehicles + sentences_names
        # render Martian predicative suffix
        def ending(noun):
            return re.search(r"[aeiouy]+?[^aeiouy]*$", noun).group(0)
        sentences = [(mar[:-1] + (ending(mar[-4]),), eng) for mar, eng in sentences]
        # get rid of PRED in English
        sentences = [(mar, eng[:-1]) for mar, eng in sentences]
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
            done = False
            ending = re.search(r"[aeiouy]+?[^aeiouy]*$", form[-4]).group(0)
            while not done:
                if random.choice([True, False]):
                    # drop PRED from predicative adjective
                    form = form[:-1]
                    done = True
                if random.choice([True, False]):
                    # tack PRED onto non-predicative adjective
                    if form[1].strip() in [self.translate(w) for w in ['green', 'red', 'nice', 'long', 'fast', 'slow']]:
                        form = form[0:2] + (ending,) + form[2:]
                        done = True
                if random.choice([True, False]):
                    # tack PRED onto non-predicative adjective
                    if form[2].strip() in [self.translate(w) for w in ['green', 'red', 'nice', 'long', 'fast', 'slow']]:
                        form = form[0:3] + (ending,) + form[3:]
                        done = True
            sentence = (tuple(form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class ErgativeAbsolutiveGrammar(CustomGrammar):
    """A grammar fragment where the subjects of intransitive verbs and the objects
    of transitive verbs are marked the same way (ergativity)."""

    def __init__(self, tokens, proper_names):
        super().__init__(tokens, proper_names)
        def monosyll(string):
            return 1 == len(list(filter(lambda x: x in 'aeiouyAEIOUY', string)))
        assert any(monosyll(s) for s in self.tokens)
        while not monosyll(self.tokens[10]) or not monosyll(self.tokens[11]):
            random.shuffle(self.tokens)
        self.lexicon = {
            'was sleeping'   : self.tokens[0],
            'were sleeping'   : self.tokens[0],
            'was walking' : self.tokens[1],
            'were walking' : self.tokens[1],
            'knew' : self.tokens[2],
            'introduced' : self.tokens[3],
            'had introduced' : self.tokens[3],
            'was introduced' : self.tokens[3],
            'were introduced' : self.tokens[3],
            'was introduced by' : self.tokens[3],
            'were introduced by' : self.tokens[3],
            'asked'  : self.tokens[4],
            'had asked'  : self.tokens[4],
            'was asked'  : self.tokens[4],
            'were asked'  : self.tokens[4],
            'was asked by'  : self.tokens[4],
            'were asked by'  : self.tokens[4],
            'the chieftain'   : self.tokens[6],
            'the chieftain of the tribe'   : self.tokens[5] + ' ' + self.tokens[6],
            'the man'  : self.tokens[7],
            'the man of the tribe'  : self.tokens[5] + ' ' + self.tokens[7],
            'and'   : self.tokens[8],
            'already'  : self.tokens[9],
            'ABS'  : self.tokens[10],
            'ERG'  : self.tokens[11]
        }

    def produce_grammatical(self, num_strings=1, polish=True):
        sentence_pattern_intransitive_1 = [
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ABS' ],
            [ '', '', ' already' ],
            [ ' was sleeping', ' was walking', ' was introduced' ]
        ]
        sentence_pattern_intransitive_2 = [
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ABS' ],
            [ ' and ' ],
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ABS' ],
            [ '', '', ' already' ],
            [ ' were sleeping', ' were walking ', ' were introduced' ],
        ]
        sentence_pattern_transitive = [
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ERG' ],
            [ '', '', ' already' ],
            [ ' knew ', ' introduced ', ' had introduced ', ' asked ', ' had asked ' ],
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ABS' ]
        ]
        sentence_pattern_passive = [
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ABS' ],
            [ '', '', ' already' ],
            [ ' was introduced by ', ' was asked by ' ],
            [ self.proper_names[0], self.proper_names[1], 'the chieftain', 'the chieftain of the tribe', 'the man', 'the man of the tribe' ],
            [ 'ERG' ]
        ]
        try:
            sentences_intransitive_1 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_intransitive_1)]
            sentences_intransitive_1 = list(set(sentences_intransitive_1))
            sentences_intransitive_1 = random.sample(sentences_intransitive_1, int(num_strings / 4 + 0.25))
            sentences_intransitive_2 = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_intransitive_2) if s[0] != s[3]]
            sentences_intransitive_2 = list(set(sentences_intransitive_2))
            sentences_intransitive_2 = random.sample(sentences_intransitive_2, int(num_strings / 4 + 0.25))
            sentences_transitive = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_transitive) if s[0] != s[4]]
            sentences_transitive = list(set(sentences_transitive))
            sentences_transitive = random.sample(sentences_transitive, int(num_strings / 4 + 0.25))
            sentences_passive = [(self.translate(s), s) for s in itertools.product(*sentence_pattern_passive) if s[0] != s[4]]
            sentences_passive = list(set(sentences_passive))
            sentences_passive = random.sample(sentences_passive, int(num_strings / 4 + 0.25))
        except ValueError:
            return None
        sentences = sentences_intransitive_1 + sentences_intransitive_2 + sentences_transitive + sentences_passive
        # fix placement of 'already' in English
        def move_already(eng):
            try:
                i = eng.index(' already')
                return eng[0:i] + eng[i+1:] + (' already',)
            except ValueError:
                return eng
        sentences = [(mar, move_already(eng)) for mar, eng in sentences]
        # remove ERG and ABS morphemes from English
        def remove_markers(eng):
            return tuple(['' if w in ['ABS', 'ERG'] else w for w in eng])
        sentences = [(mar, remove_markers(eng)) for mar, eng in sentences]
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            sentences = polish_sentences(sentences)
        random.shuffle(sentences)
        return sentences

    def produce_ungrammatical(self, num_strings=1, polish=True):
        ungrammatical_sentences = set()
        sentences = self.produce_grammatical(4, polish=False)
        while len(ungrammatical_sentences) < num_strings:
            form, meaning = sentences[0]
            sentences = sentences[1:]
            if not sentences:
                sentences = self.produce_grammatical(4, polish=False)
            done = False
            new_form = form
            while not done:
                for i, word in enumerate(form):
                    if word == self.translate('ABS') and random.choice([True, False, False]):
                        # swap ABS for ERG
                        new_form = form[:i] + (self.translate('ERG'),) + form[i+1:]
                        done = True
                    if word == self.translate('ERG') and random.choice([True, False, False]):
                        # swap ERG for ABS
                        new_form = form[:i] + (self.translate('ABS'),) + form[i+1:]
                        done = True
            sentence = (tuple(new_form), meaning)
            ungrammatical_sentences.add(sentence)
        if polish:
            # assemble real(-looking) sentences from tuples, mold into pleasing orthographic form
            ungrammatical_sentences = polish_sentences(ungrammatical_sentences)
        return ungrammatical_sentences


class NaturalnessJudgementTask(Task, Loggable):
    """See how participant rates a few plain English stimuli."""

    def ready_to_produce(self):
        return True

    def ready_to_run(self):
        return True

    def run(self):
        sentences = [
            'You caught me off guard.',
            'Little do they know, I have my own plans for these giraffes.',
            'Taco cat has a cool look.',
            'Tough though the subject matter is, it is universally relevant.',
            'Our flowers bloom outside the room.',
            'Madam in Eden, I\'m Adam.',
            'The gardener\'s friend\'s wife\'s parish priest\'s brother\'s dog got the bones from his meal.',
            'Silent stood the ancient trees.'
        ]
        self.duplicate_print(
'''And now for the easiest part! You will be asked to rate a few different English sentences as to how natural they sound on
a scale of 1 to 7. Feel free to include any further comments alongside a number, e.g. '3, sounds odd' or similar.'''
        )
        self.duplicate_print(f"You will be shown {len(sentences)} sentences total and then you're done. Press return when you are ready.")
        input()
        for i, sentence in enumerate(sentences):
            clear()
            self.duplicate_print(f"Sentence #{i+1} out of {len(sentences)}. How natural would you rate the following sentence on a scale of 1 to 7?")
            print()
            self.duplicate_print(sentence)
            while True:
                answer = ''
                while not answer:
                    answer = input()
                self.duplicate_print(answer, log_only=True)
                if not any(c.isdigit() for c in answer):
                    self.duplicate_print('Please include a numerical rating in your answer.')
                else:
                    break


class CustomExperiment(Experiment):

    settings_used = SettingsEnabled()
    settings_used.minimum_string_length = False
    settings_used.maximum_string_length = False
    settings_used.string_tokens = False
    settings_used.recursion = False

    my_grammars = [
        DefiniteArticleAgreementGrammar,
        AsymmetricArticlesGrammar,
        AccusativeMarkingAgreementGrammar,
        VerbalAgreementGrammar,
        VerbReduplicationGrammar,
        WackernagelWordOrderGrammar,
        LeadingCopulaGrammar,
        PresentParticipleGrammar,
        EvidentialGrammar,
        EchoMorphologyGrammar,
        RhymingGrammar,
        PalindromeDemonstrativeGrammar,
        PalindromePastGrammar,
        RecursiveGrammar,
        PredicativeEndingGrammar,
        ErgativeAbsolutiveGrammar
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

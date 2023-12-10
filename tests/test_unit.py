"""Unit tests to check basic expected behaviors."""

import math

from src import automaton, grammar


def test_always_pass():
    assert True


def test_grammar_exit_reachable():
    """See if at least one accepting state is always reachable."""
    g = grammar.Grammar()
    for _ in range(100):
        g.randomize()
        assert g.shortest_path_through() < math.inf


def test_grammar_exit_not_too_close():
    """See if getting to an accepting state takes enough steps."""
    g = grammar.Grammar()
    for _ in range(100):
        g.randomize()
        assert grammar.Grammar.MIN_PATH_LENGTH <= g.shortest_path_through()


def test_automaton_output_long_enough():
    """See if no output strings are below a minimum length."""
    g = grammar.Grammar()
    a = automaton.Automaton(g)
    for _ in range(100):
        g.randomize()
        output_strings = a.produce_grammatical(5)
        assert not any(len(s) < automaton.Automaton.MIN_STRING_LENGTH for s in output_strings)


def test_automaton_output_short_enough():
    """See if no output strings are above a maximum length."""
    g = grammar.Grammar()
    a = automaton.Automaton(g)
    for _ in range(100):
        g.randomize()
        output_strings = a.produce_grammatical(5)
        assert not any(len(s) > automaton.Automaton.MAX_STRING_LENGTH for s in output_strings)


def test_automaton_accepts_what_it_produced():
    """See if the automaton recognizes the same output strings that it generated."""
    g = grammar.Grammar()
    a = automaton.Automaton(g)
    for _ in range(100):
        g.randomize()
        output_strings = a.produce_grammatical(5)
        assert all(a.recognize(s) for s in output_strings)


def test_automaton_predefined_reber_1967():
    """See if the example grammar in Reber 1967 is recognized as expected."""
    reber = automaton.Automaton(grammar.REBER_1967)
    assert reber.recognize("TTS")
    assert reber.recognize("TPTS")
    assert reber.recognize("TPPTS")
    assert reber.recognize("TPPPPPTS")
    assert reber.recognize("TTXVS")
    assert reber.recognize("TPTXXVS")
    assert reber.recognize("TPTXXXVPXVS")
    assert reber.recognize("TPTXVPXXXVS")
    assert reber.recognize("TTXVPS")
    assert reber.recognize("TPTXVPXVPS")
    assert reber.recognize("TPTXVPXXVPS")
    assert reber.recognize("TPTXXXXVPXXVPS")
    assert reber.recognize("VVS")
    assert reber.recognize("VXXVS")
    assert reber.recognize("VXXXXVS")
    assert reber.recognize("VVPXVS")
    assert reber.recognize("VVPXXVS")
    assert reber.recognize("VVPS")
    assert reber.recognize("VVPXVPS")
    assert reber.recognize("VVPXXVPS")
    assert reber.recognize("VXXVPXVPS")
    assert not reber.recognize("V")
    assert not reber.recognize("TPS")
    assert not reber.recognize("VVPSV")


# def test_automaton_predefined_reber_allen_1978_I():
#     """See if the first example grammar in Reber & Allen 1978 is recognized as expected."""
#     reber_allen = automaton.Automaton(grammar.REBER_ALLEN_1978)
#     assert reber_allen.recognize("MSSSSV")
#     assert reber_allen.recognize("MSSVS")
#     assert reber_allen.recognize("MSV")
#     assert reber_allen.recognize("MSVRX")
#     assert reber_allen.recognize("MSVRXM")
#     assert reber_allen.recognize("MVRX")
#     assert reber_allen.recognize("MVRXRR")
#     assert reber_allen.recognize("MVRXSV")
#     assert reber_allen.recognize("MVRXV")
#     assert reber_allen.recognize("MVRXVS")
#     assert reber_allen.recognize("VXM")
#     assert reber_allen.recognize("VXRR")
#     assert reber_allen.recognize("VXRRM")
#     assert reber_allen.recognize("VXRRRR")
#     assert reber_allen.recognize("VXSSVS")
#     assert reber_allen.recognize("VXSVRX")
#     assert reber_allen.recognize("VXSVS")
#     assert reber_allen.recognize("VXVRX")
#     assert reber_allen.recognize("VXVRXV")
#     assert reber_allen.recognize("VXVS")
#     assert not reber_allen.recognize("VXRRS")
#     assert not reber_allen.recognize("VXX")
#     assert not reber_allen.recognize("VXRVM")
#     assert not reber_allen.recognize("XVRXRR")
#     assert not reber_allen.recognize("XSSSSV")
#     assert not reber_allen.recognize("MSVV")
#     assert not reber_allen.recognize("MMVRX")
#     assert not reber_allen.recognize("MVRSR")
#     assert not reber_allen.recognize("MSRVRX")
#     assert not reber_allen.recognize("SSVS")
#     assert not reber_allen.recognize("MSSVSR")
#     assert not reber_allen.recognize("RVS")
#     assert not reber_allen.recognize("MXVS")
#     assert not reber_allen.recognize("VRRRM")
#     assert not reber_allen.recognize("VVXRM")
#     assert not reber_allen.recognize("VXRS")
#     assert not reber_allen.recognize("MSRV")
#     assert not reber_allen.recognize("VXMRXV")
#     assert not reber_allen.recognize("MSM")
#     assert not reber_allen.recognize("SXRRM")
#     assert not reber_allen.recognize("MXVRXM")
#     assert not reber_allen.recognize("MSVRSR")
#     assert not reber_allen.recognize("SVSSXV")
#     assert not reber_allen.recognize("XRVXV")
#     assert not reber_allen.recognize("RRRXV")


def test_automaton_predefined_knowlton_squire_1994_I():
    """See if the first example grammar in Knowlton & Squire 1994 is recognized as expected."""
    knowlton_squire = automaton.Automaton(grammar.KNOWLTON_SQUIRE_1994_I)
    assert knowlton_squire.recognize("MXV")
    assert knowlton_squire.recognize("VMRV")
    assert knowlton_squire.recognize("MVXVV")
    assert knowlton_squire.recognize("VRRRM")
    assert not knowlton_squire.recognize("VV")
    assert not knowlton_squire.recognize("MMX")
    assert not knowlton_squire.recognize("MXR")
    assert not knowlton_squire.recognize("XXXV")


def test_automaton_predefined_knowlton_squire_1994_II():
    """See if the second example grammar in Knowlton & Squire 1994 is recognized as expected."""
    knowlton_squire = automaton.Automaton(grammar.KNOWLTON_SQUIRE_1994_II)
    assert knowlton_squire.recognize("TPT")
    assert knowlton_squire.recognize("FFPS")
    assert knowlton_squire.recognize("FS")
    assert knowlton_squire.recognize("TTSSSF")
    assert not knowlton_squire.recognize("FFPSSP")
    assert not knowlton_squire.recognize("PTSF")
    assert not knowlton_squire.recognize("TFT")
    assert not knowlton_squire.recognize("TPTPPT")

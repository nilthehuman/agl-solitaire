"""Unit tests to check basic expected behaviors."""

import math

from src.agl_solitaire import grammar


def test_always_pass():
    assert True


def test_grammar_exit_reachable():
    """See if at least one accepting state is always reachable."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        assert g.shortest_path_through() < math.inf


def test_grammar_exit_not_too_close():
    """See if getting to an accepting state takes enough steps."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        assert grammar.RegularGrammar.MIN_PATH_LENGTH <= g.shortest_path_through()


def test_grammar_has_cycle():
    """See if a cycle is found in a grammar that's not acyclic."""
    g = grammar.RegularGrammar()
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'M': 2},
                      {'S': 5, 'X': 6},
                      {'V': 1, 'R': 6},
                      {None: None}
                    ]
    assert g.has_cycle()


def test_grammar_has_no_cycle():
    """See if a grammar is correctly identified as acyclic."""
    g = grammar.RegularGrammar()
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'M': 6},  # <- backward edge eliminated
                      {'S': 5, 'X': 6},
                      {'V': 1, 'R': 6},
                      {None: None}
                    ]
    assert not g.has_cycle()


def test_grammar_has_loop():
    """See if a loop (a cycle of length one) is identified as a cycle as well."""
    g = grammar.RegularGrammar()
    # for all states K, all edges from K point to a state K' > K,
    # (except for the loop) so the grammar has no larger cycle
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'R': 5, 'M': 3},  # <- the loop
                      {'S': 5, 'X': 6},
                      {'R': 6},
                      {None: None}
                    ]
    assert g.has_cycle()


def test_grammar_has_no_loop():
    """See if this grammar is correctly identified as "aloopic"."""
    g = grammar.RegularGrammar()
    # for all states K, all edges from K point to a state K' > K,
    # so the grammar has no cycles
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'R': 5},  # loop removed
                      {'S': 5, 'X': 6},
                      {'R': 6},
                      {None: None}
                    ]
    assert not g.has_cycle()


def test_grammar_has_dead_cycle():
    """See if a dead cycle is found in a grammar that has one."""
    g = grammar.RegularGrammar()
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'M': 5},
                      {'S': 5, 'X': 6},
                      {'V': 1},  # (1, 3, 5)* is a dead cycle
                      {None: None}
                    ]
    assert g.has_dead_cycle()


def test_grammar_has_no_dead_cycle():
    """See if a grammar is correctly identified as acyclic."""
    g = grammar.RegularGrammar()
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'M': 2},
                      {'S': 5, 'X': 6},
                      {'V': 1, 'R': 6},
                      {None: None}
                    ]
    assert not g.has_dead_cycle()


def test_grammar_has_dead_loop():
    """See if a dead loop (a dead cycle of length one) is found as well."""
    g = grammar.RegularGrammar()
    # for all states K, all edges from K point to a state K' > K,
    # (except for the loop) so the grammar has no larger cycle
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'M': 3},  # <- the dead loop
                      {'S': 5, 'X': 6},
                      {'R': 6},
                      {None: None}
                    ]
    assert g.has_dead_cycle()


def test_grammar_has_no_dead_loop():
    """See if removing the loop helps (even if it creates a trap state)."""
    g = grammar.RegularGrammar()
    # for all states K, all edges from K point to a state K' > K,
    # so the grammar has no cycles
    g.transitions = [ {'S': 1, 'X': 2},
                      {'M': 3},
                      {'V': 4},
                      {'R': 5},  # loop removed
                      {'S': 5, 'X': 6},
                      {'R': 6},
                      {None: None}
                    ]
    assert not g.has_dead_cycle()


def test_grammar_output_long_enough():
    """See if no output strings are below a minimum length."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        output_strings = g.produce_grammatical(5)
        assert output_strings is None or not any(len(s) < grammar._MIN_STRING_LENGTH for s in output_strings)


def test_grammar_output_short_enough():
    """See if no output strings are above a maximum length."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        output_strings = g.produce_grammatical(5)
        assert output_strings is None or not any(len(s) > grammar._MAX_STRING_LENGTH for s in output_strings)


def test_grammar_accepts_grammatical():
    """See if the finite state automaton recognizes the same output strings that it generated."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        output_strings = g.produce_grammatical(5)
        assert output_strings is None or all(g.recognize(s) for s in output_strings)


def test_grammar_rejects_ungrammatical():
    """See if the finite state automaton rejects the output strings that it generated as ungrammatical."""
    g = grammar.RegularGrammar()
    for _ in range(100):
        g.randomize()
        output_strings = g.produce_ungrammatical(5)
        assert all(not g.recognize(s) for s in output_strings)


def test_grammar_predefined_reber_1967():
    """See if the example grammar in Reber 1967 is recognized as expected."""
    assert grammar.REBER_1967.recognize("TTS")
    assert grammar.REBER_1967.recognize("TPTS")
    assert grammar.REBER_1967.recognize("TPPTS")
    assert grammar.REBER_1967.recognize("TPPPPPTS")
    assert grammar.REBER_1967.recognize("TTXVS")
    assert grammar.REBER_1967.recognize("TPTXXVS")
    assert grammar.REBER_1967.recognize("TPTXXXVPXVS")
    assert grammar.REBER_1967.recognize("TPTXVPXXXVS")
    assert grammar.REBER_1967.recognize("TTXVPS")
    assert grammar.REBER_1967.recognize("TPTXVPXVPS")
    assert grammar.REBER_1967.recognize("TPTXVPXXVPS")
    assert grammar.REBER_1967.recognize("TPTXXXXVPXXVPS")
    assert grammar.REBER_1967.recognize("VVS")
    assert grammar.REBER_1967.recognize("VXXVS")
    assert grammar.REBER_1967.recognize("VXXXXVS")
    assert grammar.REBER_1967.recognize("VVPXVS")
    assert grammar.REBER_1967.recognize("VVPXXVS")
    assert grammar.REBER_1967.recognize("VVPS")
    assert grammar.REBER_1967.recognize("VVPXVPS")
    assert grammar.REBER_1967.recognize("VVPXXVPS")
    assert grammar.REBER_1967.recognize("VXXVPXVPS")
    assert not grammar.REBER_1967.recognize("V")
    assert not grammar.REBER_1967.recognize("TPS")
    assert not grammar.REBER_1967.recognize("VVPSV")


# def test_grammar_predefined_reber_allen_1978_I():
#     """See if the first example grammar in Reber & Allen 1978 is recognized as expected."""
#     assert grammar.REBER_ALLEN_1978.recognize("MSSSSV")
#     assert grammar.REBER_ALLEN_1978.recognize("MSSVS")
#     assert grammar.REBER_ALLEN_1978.recognize("MSV")
#     assert grammar.REBER_ALLEN_1978.recognize("MSVRX")
#     assert grammar.REBER_ALLEN_1978.recognize("MSVRXM")
#     assert grammar.REBER_ALLEN_1978.recognize("MVRX")
#     assert grammar.REBER_ALLEN_1978.recognize("MVRXRR")
#     assert grammar.REBER_ALLEN_1978.recognize("MVRXSV")
#     assert grammar.REBER_ALLEN_1978.recognize("MVRXV")
#     assert grammar.REBER_ALLEN_1978.recognize("MVRXVS")
#     assert grammar.REBER_ALLEN_1978.recognize("VXM")
#     assert grammar.REBER_ALLEN_1978.recognize("VXRR")
#     assert grammar.REBER_ALLEN_1978.recognize("VXRRM")
#     assert grammar.REBER_ALLEN_1978.recognize("VXRRRR")
#     assert grammar.REBER_ALLEN_1978.recognize("VXSSVS")
#     assert grammar.REBER_ALLEN_1978.recognize("VXSVRX")
#     assert grammar.REBER_ALLEN_1978.recognize("VXSVS")
#     assert grammar.REBER_ALLEN_1978.recognize("VXVRX")
#     assert grammar.REBER_ALLEN_1978.recognize("VXVRXV")
#     assert grammar.REBER_ALLEN_1978.recognize("VXVS")
#     assert not grammar.REBER_ALLEN_1978.recognize("VXRRS")
#     assert not grammar.REBER_ALLEN_1978.recognize("VXX")
#     assert not grammar.REBER_ALLEN_1978.recognize("VXRVM")
#     assert not grammar.REBER_ALLEN_1978.recognize("XVRXRR")
#     assert not grammar.REBER_ALLEN_1978.recognize("XSSSSV")
#     assert not grammar.REBER_ALLEN_1978.recognize("MSVV")
#     assert not grammar.REBER_ALLEN_1978.recognize("MMVRX")
#     assert not grammar.REBER_ALLEN_1978.recognize("MVRSR")
#     assert not grammar.REBER_ALLEN_1978.recognize("MSRVRX")
#     assert not grammar.REBER_ALLEN_1978.recognize("SSVS")
#     assert not grammar.REBER_ALLEN_1978.recognize("MSSVSR")
#     assert not grammar.REBER_ALLEN_1978.recognize("RVS")
#     assert not grammar.REBER_ALLEN_1978.recognize("MXVS")
#     assert not grammar.REBER_ALLEN_1978.recognize("VRRRM")
#     assert not grammar.REBER_ALLEN_1978.recognize("VVXRM")
#     assert not grammar.REBER_ALLEN_1978.recognize("VXRS")
#     assert not grammar.REBER_ALLEN_1978.recognize("MSRV")
#     assert not grammar.REBER_ALLEN_1978.recognize("VXMRXV")
#     assert not grammar.REBER_ALLEN_1978.recognize("MSM")
#     assert not grammar.REBER_ALLEN_1978.recognize("SXRRM")
#     assert not grammar.REBER_ALLEN_1978.recognize("MXVRXM")
#     assert not grammar.REBER_ALLEN_1978.recognize("MSVRSR")
#     assert not grammar.REBER_ALLEN_1978.recognize("SVSSXV")
#     assert not grammar.REBER_ALLEN_1978.recognize("XRVXV")
#     assert not grammar.REBER_ALLEN_1978.recognize("RRRXV")


def test_grammar_predefined_knowlton_squire_1994_I():
    """See if the first example grammar in Knowlton & Squire 1994 is recognized as expected."""
    assert grammar.KNOWLTON_SQUIRE_1994_I.recognize("MXV")
    assert grammar.KNOWLTON_SQUIRE_1994_I.recognize("VMRV")
    assert grammar.KNOWLTON_SQUIRE_1994_I.recognize("MVXVV")
    assert grammar.KNOWLTON_SQUIRE_1994_I.recognize("VRRRM")
    assert not grammar.KNOWLTON_SQUIRE_1994_I.recognize("VV")
    assert not grammar.KNOWLTON_SQUIRE_1994_I.recognize("MMX")
    assert not grammar.KNOWLTON_SQUIRE_1994_I.recognize("MXR")
    assert not grammar.KNOWLTON_SQUIRE_1994_I.recognize("XXXV")


def test_grammar_predefined_knowlton_squire_1994_II():
    """See if the second example grammar in Knowlton & Squire 1994 is recognized as expected."""
    assert grammar.KNOWLTON_SQUIRE_1994_II.recognize("TPT")
    assert grammar.KNOWLTON_SQUIRE_1994_II.recognize("FFPS")
    assert grammar.KNOWLTON_SQUIRE_1994_II.recognize("FS")
    assert grammar.KNOWLTON_SQUIRE_1994_II.recognize("TTSSSF")
    assert not grammar.KNOWLTON_SQUIRE_1994_II.recognize("FFPSSP")
    assert not grammar.KNOWLTON_SQUIRE_1994_II.recognize("PTSF")
    assert not grammar.KNOWLTON_SQUIRE_1994_II.recognize("TFT")
    assert not grammar.KNOWLTON_SQUIRE_1994_II.recognize("TPTPPT")

agl-solitaire
=============

Artificial Grammar Learning is an important experimental paradigm in linguistics
and cognitive science.[^1] The subject is shown a list of short strings of
letters generated using a regular grammar chosen by the experimenter. The
subject is then asked to make grammaticality judgements about a second set of
strings. The experiment is sometimes performed in a repeat design.

I wanted to try the experiment hands on myself to get a sense of how difficult
it is, what kinds of grammars are easier to learn, and whether trying to
consciously figure out the underlying regular grammar helps boost performance.
However I obviously could not be the experimenter and the subject at the same
time, so I had to leave it to a computer to pick a grammar and test me on it.

The result is this simple, easy-to-use command line application that lets you
play the standard AGL game against the computer. First you will be presented a
list of 20 unique training stimuli which all conform to a hidden grammar chosen
at random. In the testing phase you will be asked to judge the validity of 40
different test strings one by one, half of which are grammatical and the other
half ungrammatical. After completing the test the underlying formal grammar will
be revealed along with the correct answers and your results.

Everything that happens on screen during the game is also automatically recorded
in a file called `agl_session.log` by default (you can turn this off if you
wish). My own sessions are recorded in `arato.log` for the sake of analysis.

See ./agl-solitaire --help for a more detailed explanation of options and
preferences.

The software is released under the popular open source MIT License.

[^1]: Reber, A. S. (1967). Implicit learning of artificial grammars. Journal of
Verbal Learning and Verbal Behavior, 5, 855-863.

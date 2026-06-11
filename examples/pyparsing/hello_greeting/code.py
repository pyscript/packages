"""
A first look at pyparsing: build a tiny grammar in pure Python.

pyparsing lets you compose grammars from class instances, using
'+' for sequence and '|' for alternatives. The result of parsing
is a ParseResults object, which behaves like a list and (when you
add results names) like a dict.
"""
from IPython.core.display import display, HTML
# Package imports for this example.
import pyparsing as pp
from pyparsing import Word, alphas


heading("1. Parsing a friendly greeting")
note(
    "Our grammar says: a word, then a comma, then another word, "
    "then an exclamation mark. pyparsing handles whitespace for us."
)

# Word(alphas) matches a run of letters. The literal strings "," and "!"
# match themselves. The '+' operator concatenates expressions.
greeting = Word(alphas) + "," + Word(alphas) + "!"

samples = [
    "Hello, World!",
    "Hi,Friend!",          # no spaces
    "  Hey ,   Ada !  ",   # extra whitespace everywhere
]

for text in samples:
    parsed = greeting.parse_string(text)
    note(f"<code>{text!r}</code> &rarr; <code>{list(parsed)}</code>")

heading("2. Naming parts of the match")
note(
    "Attach names with set_results_name (or the shorthand '()' call). "
    "Named pieces become attributes and dict keys on the result."
)

named_greeting = (
    Word(alphas)("salutation")
    + ","
    + Word(alphas)("addressee")
    + "!"
)

result = named_greeting.parse_string("Howdy, Partner!")
note(f"As a list: <code>{list(result)}</code>")
note(f"result.salutation = <code>{result.salutation!r}</code>")
note(f"result.addressee  = <code>{result.addressee!r}</code>")
note(f"As a dict: <code>{result.as_dict()}</code>")

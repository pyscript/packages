"""
A first taste of arrr: turning plain English into Pirate-ish.

The whole package is essentially one function, `translate`, which
takes a string of English and returns a saltier, more piratical
version of it. Sometimes it will even interject with a piratical
saying of its own. That's not a bug -- it's the whole point.

Docs and source: https://github.com/ntoll/arrr
"""
from IPython.core.display import display, HTML
from arrr import translate

heading("A polite greeting, translated")

english = "Hello there. How are you today? I hope you are well."
pirate = translate(english)

note("Original English:")
display(HTML(f"<blockquote>{english}</blockquote>"), append=True)

note("Pirate-ish translation:")
display(HTML(f"<blockquote>{pirate}</blockquote>"), append=True)

# Because arrr sometimes interjects with random pirate sayings, you'll
# get slightly different output every time you run this. Try clicking
# the run button a few times!

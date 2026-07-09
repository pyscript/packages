"""
A first look at texttable: build simple ASCII tables in pure Python.

Texttable is handy whenever you want neat, monospaced output in a
terminal, a log file, an email, or anywhere a plain string is more
useful than a styled DataFrame. See:
https://github.com/foutaise/texttable/
"""
from IPython.core.display import display, HTML
from texttable import Texttable

heading("A team roster as an ASCII table")
note(
    "Create a Texttable, hand it rows where the first row is the "
    "header, and call draw() to get a string. The first column "
    "shows multi-line cells -- newlines inside a cell just work."
)

roster = Texttable()
roster.set_cols_align(["l", "r", "c"])
roster.set_cols_valign(["t", "m", "b"])
roster.add_rows([
    ["Name", "Age", "Nickname"],
    ["Mr\nXavier\nHuon", 32, "Xav'"],
    ["Mr\nBaptiste\nClement", 1, "Baby"],
    ["Mme\nLouise\nBourgeau", 28, "Lou\n\nLoue"],
])

# draw() returns the whole table as one string. We wrap it in <pre>
# so the browser preserves the monospaced layout.
rendered = roster.draw()
display(HTML(f"<pre>{rendered}</pre>"), append=True)

note(
    "You can also print(roster.draw()) in a regular terminal "
    "script -- the output is just text."
)

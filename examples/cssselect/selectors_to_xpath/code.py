"""
A first look at cssselect: turning familiar CSS selectors into the
XPath 1.0 expressions that XML/HTML query engines (such as lxml) can
evaluate.

Documentation: https://cssselect.readthedocs.io
"""
import cssselect
from IPython.core.display import display, HTML

# A small gallery of CSS selectors that web developers see every day.
# Each one targets a different kind of pattern.
selectors = [
    "div",                          # all <div> elements
    "a.external",                   # <a> with class "external"
    "ul#menu > li",                 # direct children of #menu
    "input[type='email']",          # attribute equality
    "p:first-child",                # structural pseudo-class
    "h1, h2, h3",                   # selector list
    "article p:nth-of-type(2)",     # positional pseudo-class
]

heading("CSS selectors translated to XPath")
note(
    "cssselect.GenericTranslator turns each CSS3 selector into an "
    "equivalent XPath 1.0 expression you can run against any XML "
    "or HTML document."
)

translator = cssselect.GenericTranslator()

rows = ["<tr><th>CSS selector</th><th>XPath</th></tr>"]
for css in selectors:
    xpath = translator.css_to_xpath(css)
    rows.append(f"<tr><td><code>{css}</code></td><td><code>{xpath}</code></td></tr>")

display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

# HTMLTranslator knows about HTML-specific quirks: case-insensitive
# tag and attribute names, the :link pseudo-class, and so on.
note(
    "For HTML documents, prefer HTMLTranslator. It lower-cases tag "
    "names and understands HTML-only pseudo-classes like :link."
)

html_translator = cssselect.HTMLTranslator()
for css in ["A.external", "a:link", "INPUT[TYPE='email']"]:
    xpath = html_translator.css_to_xpath(css)
    note(f"<code>{css}</code> &rarr; <code>{xpath}</code>")

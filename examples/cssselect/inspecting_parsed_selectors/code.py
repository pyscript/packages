# ---------------------------------------------------------------------
# Beyond translation: inspect the abstract syntax tree that cssselect
# builds when it parses a selector. This is how you'd build tooling
# such as linters, selector simplifiers, or custom query engines.
# ---------------------------------------------------------------------

heading("Parsing a selector into a tree")
note(
    "cssselect.parse() returns a list of Selector objects, one per "
    "comma-separated selector. Each Selector wraps a parsed tree "
    "you can walk."
)

source = "div.card > a.external[href^='https']:hover, footer p:last-child"
parsed = cssselect.parse(source)

note(f"Parsed <code>{source}</code> into {len(parsed)} top-level selector(s):")
for selector in parsed:
    note(
        f"&bull; specificity {selector.specificity()} &middot; "
        f"pseudo-element: {selector.pseudo_element!r} &middot; "
        f"tree: <code>{selector.parsed_tree!r}</code>"
    )

# Specificity is a 3-tuple (id, class/attr/pseudo-class, type/pseudo-element).
# Higher tuples win in CSS cascade conflicts.
heading("Comparing specificities")
candidates = [
    "p",
    ".note",
    "p.note",
    "#sidebar p.note",
    "#sidebar p.note:hover",
]
rows = ["<tr><th>Selector</th><th>Specificity</th></tr>"]
for css in candidates:
    (selector,) = cssselect.parse(css)
    rows.append(
        f"<tr><td><code>{css}</code></td>"
        f"<td>{selector.specificity()}</td></tr>"
    )
display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

# Unsupported or malformed selectors raise SelectorError, which is the
# common base class for SelectorSyntaxError and ExpressionError.
heading("Handling invalid selectors")
note(
    "Catch cssselect.SelectorError to handle both syntax errors and "
    "selectors that can't be expressed as XPath."
)

bad_selectors = ["div >", "p::made-up-pseudo-element", "a:nth-child(odd)"]
for css in bad_selectors:
    try:
        xpath = cssselect.HTMLTranslator().css_to_xpath(css)
        note(f"<code>{css}</code> &rarr; <code>{xpath}</code>")
    except cssselect.SelectorError as exc:
        note(f"<code>{css}</code> &rarr; <em>{type(exc).__name__}: {exc}</em>")

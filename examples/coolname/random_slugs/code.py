"""
A first look at coolname: produce friendly random identifiers like
'wealthy-athletic-swift-of-tempest' for use as project names, room
codes, temporary usernames, or container labels.

Docs: https://coolname.readthedocs.io/en/latest/
"""
from IPython.core.display import display, HTML

heading("1. A handful of random slugs")
note(
    "<code>generate_slug()</code> returns a hyphenated, "
    "Django-friendly string. Without arguments it leans toward "
    "longer (4-word) names."
)

slugs = [generate_slug() for _ in range(5)]
display(HTML("<ul>" + "".join(f"<li><code>{s}</code></li>" for s in slugs) + "</ul>"),
        append=True)

heading("2. Pick the length you want")
note(
    "Pass 2, 3, or 4 to control how many real words appear. "
    "Connectors like 'of' and 'the' don't count toward the length."
)

for length in (2, 3, 4):
    note(f"Length {length}: <code>{generate_slug(length)}</code>")

heading("3. Names as token lists")
note(
    "<code>generate()</code> returns the raw word list, so you can "
    "join, capitalize, or otherwise reshape it however you like."
)

tokens = generate()
note(f"Raw tokens: <code>{tokens}</code>")
note(f"Spaced: <code>{' '.join(tokens)}</code>")
note(f"CamelCase: <code>{''.join(w.capitalize() for w in tokens)}</code>")

heading("4. Just how many names are there?")
total = get_combinations_count()
note(
    f"The default vocabulary supports "
    f"<strong>{total:,}</strong> distinct names. "
    "Plenty of room for unique identifiers."
)

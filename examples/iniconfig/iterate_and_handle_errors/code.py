# ---------------------------------------------------------------------
# Iterating an IniConfig and dealing with malformed input.
# ---------------------------------------------------------------------

heading("Iterating sections and items")
note(
    "An <code>IniConfig</code> is iterable: looping over it yields "
    "sections in the order they appeared in the source. Each "
    "section in turn yields its <code>(name, value)</code> pairs "
    "via <code>.items()</code>. iniconfig also supports multi-line "
    "values -- just indent the continuation lines."
)

ini_source = """
[fiction]
title = The Left Hand of Darkness
author = Ursula K. Le Guin
tags = sci-fi,classic

[non_fiction]
title = The Making of the Atomic Bomb
author = Richard Rhodes

[poetry]
title = Ariel
author = Sylvia Plath
# A multi-line value: indent continuation lines.
notes =
    Published posthumously in 1965.
    Restored edition followed in 2004.
"""

shelf = iniconfig.IniConfig("shelf.ini", data=ini_source)

# Membership tests work on section names.
note(f"Has 'poetry' section? <code>{'poetry' in shelf}</code>")
note(f"Has 'cookbooks' section? <code>{'cookbooks' in shelf}</code>")

# Walk every section and dump its items as a small HTML list.
rows = []
for section in shelf:
    items_html = "".join(
        f"<li><code>{name}</code> = {value!r}</li>"
        for name, value in section.items()
    )
    rows.append(f"<h3>[{section.name}]</h3><ul>{items_html}</ul>")
display(HTML("".join(rows)), append=True)

# ---------------------------------------------------------------------
# Parse errors carry the line number, which makes them easy to
# surface to a user.
# ---------------------------------------------------------------------
heading("Parse errors point at the offending line")
note(
    "If the source is malformed, iniconfig raises "
    "<code>ParseError</code> with the file label and line number. "
    "The example below has a stray key outside any section."
)

broken_source = """
[ok]
key = value

stray_key = oops, no section above me

[also_ok]
foo = bar
"""

try:
    iniconfig.IniConfig("broken.ini", data=broken_source)
except iniconfig.ParseError as err:
    note(
        f"Caught <code>ParseError</code>: <code>{err}</code>"
    )

# Duplicate section names are also rejected.
duplicate_source = """
[server]
host = a

[server]
host = b
"""

try:
    iniconfig.IniConfig("dup.ini", data=duplicate_source)
except iniconfig.ParseError as err:
    note(
        f"Duplicate sections raise too: <code>{err}</code>"
    )

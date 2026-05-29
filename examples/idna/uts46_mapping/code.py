# ---------------------------------------------------------------------
# Real-world input is messy: users type capital letters, paste from
# documents with full-width characters, and so on. Strict IDNA 2008
# rejects most of this. UTS #46 ("Unicode IDNA Compatibility
# Processing") normalizes input first -- lowercasing, mapping
# compatibility characters -- and then applies IDNA encoding.
# ---------------------------------------------------------------------

heading("Strict IDNA vs. UTS #46 compatibility mapping")

messy_inputs = [
    "Königsgäßchen",          # Mixed case German
    "ΠΑΡΆΔΕΙΓΜΑ.ΕΛ",          # Upper-case Greek
    "Bücher.DE",              # Mixed case with umlaut
]

rows = ["<table border='1' cellpadding='6'><tr>"
        "<th>Input</th><th>Strict IDNA 2008</th>"
        "<th>With <code>uts46=True</code></th></tr>"]

for raw in messy_inputs:
    # Try the strict path first; capture the error message if it fails.
    try:
        strict = idna.encode(raw).decode("ascii")
        strict_cell = f"<code>{strict}</code>"
    except idna.IDNAError as err:
        strict_cell = f"<em style='color:#b00'>{type(err).__name__}</em>"

    # The UTS #46 path lowercases and maps compatibility characters
    # before encoding, so it handles user-friendly input gracefully.
    lenient = idna.encode(raw, uts46=True).decode("ascii")
    rows.append(
        f"<tr><td>{raw}</td><td>{strict_cell}</td>"
        f"<td><code>{lenient}</code></td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

note(
    "Strict mode follows IDNA 2008 verbatim and rejects capital "
    "letters and certain compatibility characters. UTS #46 mapping "
    "is what most browsers and resolvers actually do."
)

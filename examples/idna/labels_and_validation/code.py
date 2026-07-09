# ---------------------------------------------------------------------
# A domain is a sequence of labels separated by dots. The `alabel` and
# `ulabel` helpers operate on a single label at a time, which is handy
# when you're building or inspecting domain names piece by piece. The
# specific exception subclasses tell you *why* a label was rejected.
# ---------------------------------------------------------------------

heading("Converting individual labels")

# Build a domain label-by-label. Each call validates one piece.
parts = ["शॉप", "मुंबई", "भारत"]   # Hindi: "shop.mumbai.bharat"
encoded_parts = [idna.alabel(p).decode("ascii") for p in parts]
domain_ascii = ".".join(encoded_parts)

note("Hindi labels encoded individually with <code>idna.alabel</code>:")
rows = ["<table border='1' cellpadding='6'><tr>"
        "<th>Unicode label</th><th>A-label</th></tr>"]
for unicode_part, ascii_part in zip(parts, encoded_parts):
    rows.append(
        f"<tr><td>{unicode_part}</td><td><code>{ascii_part}</code></td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

display(HTML(f"<p>Joined domain: <code>{domain_ascii}</code></p>"), append=True)

# And the round-trip back via ulabel:
recovered = ".".join(idna.ulabel(p) for p in encoded_parts)
display(HTML(f"<p>Decoded back: <strong>{recovered}</strong></p>"), append=True)

# ---------------------------------------------------------------------
# Things that should fail -- and the exception types that tell you why.
# ---------------------------------------------------------------------

heading("How invalid input is rejected")

bad_inputs = [
    ("hello world", "spaces are not valid in domain labels"),
    ("café.com", "U+00E9 is not allowed under strict IDNA 2008"),
    ("a" * 64, "labels longer than 63 octets are rejected"),
    ("☃.example", "symbols (here, a snowman) are forbidden"),
]

rows = ["<table border='1' cellpadding='6'><tr>"
        "<th>Input</th><th>Why it might fail</th>"
        "<th>Exception</th></tr>"]
for value, why in bad_inputs:
    try:
        idna.encode(value)
        outcome = "<em>(unexpectedly accepted)</em>"
    except idna.IDNAError as err:
        # Every idna error inherits from IDNAError; the specific
        # subclass narrows down the cause.
        outcome = f"<code>{type(err).__name__}</code>: {err}"
    shown = value if len(value) < 30 else value[:27] + "..."
    rows.append(
        f"<tr><td><code>{shown}</code></td><td>{why}</td>"
        f"<td>{outcome}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

note(
    "Catch <code>idna.IDNAError</code> to handle any conversion "
    "failure, or catch a specific subclass like "
    "<code>InvalidCodepoint</code> or <code>IDNABidiError</code> "
    "for finer control."
)

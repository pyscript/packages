# ---------------------------------------------------------------------
# Decoding web payloads: BOM sniffing and fallback labels.
# ---------------------------------------------------------------------

heading("Decoding bytes the way a browser would")
note(
    "The standard says: if a byte stream starts with a UTF-8, "
    "UTF-16-LE, or UTF-16-BE BOM, that BOM wins, regardless of "
    "what the HTTP header or meta tag claims. Otherwise, fall "
    "back to the declared label. <code>webencodings.decode</code> "
    "implements exactly that."
)

# A few payloads representing different sources on the web.
samples = [
    (
        "UTF-8 page with a BOM, mislabelled as iso-8859-1",
        "\ufeffCafé — déjà vu".encode("utf-8"),
        "iso-8859-1",
    ),
    (
        "UTF-16-LE page with a BOM, no charset declared",
        "\ufeffHello, BOM!".encode("utf-16-le"),
        None,  # no declared label; fallback will be used
    ),
    (
        "windows-1252 page labelled latin1 (smart quotes)",
        b"She said \x93hi\x94 and left.",
        "latin1",
    ),
    (
        "Plain UTF-8 page, no BOM, correctly labelled",
        "naïve façade".encode("utf-8"),
        "utf-8",
    ),
]

# `decode(input, fallback_encoding)` returns a (text, encoding) pair
# so you can see which encoding was actually used.
rows = [
    "<tr><th>Source</th><th>Used</th><th>Decoded text</th></tr>"
]
for description, payload, declared in samples:
    fallback = webencodings.lookup(declared) if declared else \
        webencodings.lookup("windows-1252")
    text, used = webencodings.decode(payload, fallback)
    rows.append(
        f"<tr><td>{description}</td>"
        f"<td><code>{used.name}</code></td>"
        f"<td><code>{text!r}</code></td></tr>"
    )
display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

note(
    "In the first row the declared label was <code>iso-8859-1</code>, "
    "but the UTF-8 BOM took precedence and the page decoded "
    "correctly as UTF-8. That single rule prevents a huge class of "
    "mojibake bugs when scraping or rendering legacy web content."
)

# Encoding back out is symmetric: use `webencodings.encode`.
heading("Round-tripping back to bytes", level=3)
encoded_bytes = webencodings.encode("Café — déjà vu", "utf-8")
note(
    "<code>webencodings.encode('Café — déjà vu', 'utf-8')</code> "
    f"&rarr; <code>{encoded_bytes!r}</code>"
)

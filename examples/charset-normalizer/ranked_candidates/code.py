# ---------------------------------------------------------------------
# Multiple plausible encodings: walking the candidate list.
# ---------------------------------------------------------------------

heading("When more than one encoding fits")
note(
    "Some byte sequences decode without errors under several different "
    "encodings, often producing identical or near-identical text. "
    "<code>from_bytes(...)</code> returns every plausible candidate, "
    "ranked from most to least likely."
)

# A short French phrase with accented characters, encoded as cp1252.
# This same byte sequence is also valid under several other Western
# encodings (latin_1, iso8859_15, ...), and they often produce the
# very same characters.
phrase = "Café à Montréal — très belle journée!"
raw = phrase.encode("cp1252")

results = from_bytes(raw)

heading("All candidate matches", level=3)
note(f"charset-normalizer found {len(results)} viable candidate(s).")

# CharsetMatches is iterable, indexable, and sortable. Each item is a
# CharsetMatch carrying chaos (lower is cleaner), coherence (higher
# is more language-like), and the encoding name plus its aliases.
rows = ["<table border='1' cellpadding='4' style='border-collapse: collapse'>"]
rows.append(
    "<tr><th>Rank</th><th>Encoding</th><th>Aliases</th>"
    "<th>Chaos</th><th>Coherence</th><th>Language</th></tr>"
)
for rank, match in enumerate(results, start=1):
    aliases = ", ".join(match.encoding_aliases) or "&mdash;"
    rows.append(
        f"<tr><td>{rank}</td><td><code>{match.encoding}</code></td>"
        f"<td>{aliases}</td><td>{match.chaos:.3f}</td>"
        f"<td>{match.coherence:.3f}</td><td>{match.language}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

heading("Confirming the decoded text matches", level=3)
best = results.best()
note(
    f"Best match decodes to: <em>{str(best)}</em><br>"
    f"Round-trip equal to original phrase? "
    f"<strong>{str(best) == phrase}</strong>"
)

# You can also normalize directly to UTF-8 bytes for safe storage.
utf8_bytes = best.output(encoding="utf_8")
note(
    f"Re-encoded as UTF-8: {len(utf8_bytes)} bytes "
    f"(was {len(raw)} bytes as <code>{best.encoding}</code>)."
)

# ---------------------------------------------------------------------
# A real-world flavor: extracting structured fields from log lines.
# ---------------------------------------------------------------------
#
# We'll define a grammar for lines like:
#
#   2026-04-15 09:31:02 [INFO] user=ada action="login" ms=42
#
# and pull out timestamp, level, and a dictionary of key=value pairs.

heading("Defining the grammar piece by piece")

# Date and time, built from digit runs joined by literal separators.
# Combine merges adjacent matches into one string token.
integer = Word(nums)
date = Combine(integer + "-" + integer + "-" + integer)
time = Combine(integer + ":" + integer + ":" + integer)
timestamp = Combine(date + " " + time)("timestamp")

# Log level in square brackets. Suppress(...) matches but discards.
level = (
    Suppress("[")
    + one_of("DEBUG INFO WARN ERROR")("level")
    + Suppress("]")
)

# A key=value pair. Values can be bare words, quoted strings, or numbers.
key = Word(alphas, alphanums + "_")
bare_value = Word(alphanums + "_.-")
quoted_value = QuotedString('"')
value = quoted_value | pyparsing_common.number | bare_value
pair = Group(key("key") + Suppress("=") + value("value"))

pairs = Group(OneOrMore(pair))("fields")

log_line = timestamp + level + pairs

heading("Parsing some log lines")

lines = [
    '2026-04-15 09:31:02 [INFO] user=ada action="login" ms=42',
    '2026-04-15 09:31:07 [WARN] user=ada action="slow_query" ms=1873 table=orders',
    '2026-04-15 09:31:12 [ERROR] user=bob action="checkout" code=500 reason="db timeout"',
]

rows = [
    "<table><tr><th>Timestamp</th><th>Level</th><th>Fields</th></tr>"
]
for line in lines:
    parsed = log_line.parse_string(line, parse_all=True)
    fields = {p.key: p.value for p in parsed.fields}
    rows.append(
        f"<tr><td><code>{parsed.timestamp}</code></td>"
        f"<td><strong>{parsed.level}</strong></td>"
        f"<td><code>{fields}</code></td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

heading("Scanning a larger blob of text")
note(
    "scan_string walks through arbitrary text and yields every match "
    "of the grammar, along with its location. Great for extracting "
    "structured data from messy input."
)

blob = """
Some preamble that isn't a log line at all.
2026-04-15 09:31:02 [INFO] user=ada action="login" ms=42
... noise in between ...
2026-04-15 09:31:99 [INFO] this line is malformed and will be skipped
2026-04-15 09:32:00 [INFO] user=ada action="logout" ms=8
"""

found = []
for tokens, start, end in log_line.scan_string(blob):
    fields = {p.key: p.value for p in tokens.fields}
    found.append((tokens.timestamp, tokens.level, fields))

note(f"Found <strong>{len(found)}</strong> well-formed log entries:")
for ts, lvl, fs in found:
    display(HTML(f"<code>{ts} [{lvl}] {fs}</code>"), append=True)

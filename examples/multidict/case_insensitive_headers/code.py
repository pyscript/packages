# ---------------------------------------------------------------------
# CIMultiDict: case-insensitive keys for HTTP-style headers.
# ---------------------------------------------------------------------

heading("HTTP headers with CIMultiDict")
note(
    "HTTP header names are case-insensitive: <code>Content-Type</code>, "
    "<code>content-type</code>, and <code>CONTENT-TYPE</code> all refer "
    "to the same header. <code>CIMultiDict</code> handles this for you "
    "while still allowing duplicates (e.g. multiple <code>Set-Cookie</code> "
    "headers)."
)

headers = CIMultiDict([
    ("Content-Type", "application/json"),
    ("Cache-Control", "no-cache"),
    ("Set-Cookie", "session=abc123; Path=/"),
    ("Set-Cookie", "theme=dark; Path=/"),
])

# Lookup is case-insensitive on the way in...
note(
    "Lookups ignore case: "
    f"<code>headers['content-type']</code> = "
    f"<code>{headers['content-type']!r}</code>"
)
note(
    f"<code>'CACHE-CONTROL' in headers</code> = "
    f"<strong>{'CACHE-CONTROL' in headers}</strong>"
)

# ...and getall() still returns every matching value.
heading("Multiple Set-Cookie headers")
display(headers.getall("set-cookie"), append=True)

# Adding a duplicate-cased entry merges into the same logical header.
headers.add("X-Request-Id", "req-001")
headers.add("x-request-id", "req-002")
note("Two adds with different casing, one logical header:")
display(headers.getall("X-Request-Id"), append=True)

# istr is an interned, case-preserving string type. Using it as a key
# is a bit faster than re-hashing a plain str on every lookup, and it
# preserves the original casing for display.
heading("istr: case-insensitive but case-preserving")
content_type = istr("Content-Type")
note(
    f"<code>istr</code> repr keeps original casing: "
    f"<code>{content_type!r}</code>, but compares case-insensitively: "
    f"<code>istr('Content-Type') == 'CONTENT-TYPE'</code> is "
    f"<strong>{content_type == 'CONTENT-TYPE'}</strong>"
)

# Compare with a plain MultiDict to see why CI matters for headers.
heading("Why not just use MultiDict?")
plain = MultiDict([("Content-Type", "application/json")])
note(
    "A plain <code>MultiDict</code> is case-sensitive, so "
    "<code>'content-type' in plain</code> is "
    f"<strong>{'content-type' in plain}</strong> -- not what you want "
    "for HTTP headers."
)

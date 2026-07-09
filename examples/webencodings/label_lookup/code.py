"""
A first look at `webencodings`.

The WHATWG Encoding standard defines how browsers map encoding
*labels* (the strings that appear in HTTP headers and HTML meta
tags) to actual encodings. Many of these mappings are surprising
for historical, web-compatibility reasons. The `webencodings`
package implements those rules so Python tools can decode legacy
web content the same way a browser would.

Docs: https://pythonhosted.org/webencodings/
"""
from IPython.core.display import display, HTML

import webencodings


heading("Encoding labels and what they really mean")
note(
    "On the web, lots of encoding labels are aliases for something "
    "else. The classic surprise: a page that claims to be "
    "<code>iso-8859-1</code> or <code>US-ASCII</code> is actually "
    "decoded as <code>windows-1252</code>. Let's confirm that with "
    "<code>webencodings.lookup</code>."
)

# `lookup` returns an Encoding object (or None for unknown labels).
# The .name attribute is the canonical WHATWG name.
labels_seen_in_the_wild = [
    "utf-8",
    "UTF8",
    "  iso-8859-1  ",   # whitespace and case are ignored
    "us-ascii",
    "latin1",
    "windows-1252",
    "shift_jis",
    "gb2312",
    "made-up-encoding",
]

heading("What each label maps to", level=3)
rows = ["<tr><th>Label</th><th>Canonical name</th></tr>"]
for label in labels_seen_in_the_wild:
    encoding = webencodings.lookup(label)
    canonical = encoding.name if encoding else "<em>(unknown)</em>"
    rows.append(
        f"<tr><td><code>{label!r}</code></td>"
        f"<td><code>{canonical}</code></td></tr>"
    )
display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

note(
    "Notice how <code>iso-8859-1</code>, <code>us-ascii</code>, and "
    "<code>latin1</code> all resolve to <code>windows-1252</code>. "
    "That's the web-compat behaviour the standard mandates."
)

# Decoding through the Encoding object uses Python's own codecs
# under the hood, but with the right web-flavoured choice.
sample_bytes = b"Caf\xe9 \x93hello\x94"  # 0x93/0x94 are smart quotes
# in windows-1252, but undefined in strict iso-8859-1.
encoding = webencodings.lookup("iso-8859-1")
text = encoding.codec_info.decode(sample_bytes)[0]
note(
    f"Decoding {sample_bytes!r} as <code>iso-8859-1</code> via "
    f"webencodings yields: <code>{text!r}</code> "
    "(smart quotes survive, because we're really using "
    "windows-1252)."
)

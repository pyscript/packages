"""
A first look at the `idna` package.

Internationalized domain names use characters outside ASCII (think
Japanese, Cyrillic, Arabic). DNS itself only speaks ASCII, so each
Unicode label gets translated into an ASCII-compatible form starting
with `xn--`. The `idna` package handles that translation in both
directions, following the modern IDNA 2008 specification.

Docs: https://github.com/kjd/idna
"""
from IPython.core.display import display, HTML

import idna

# A small address book of domains in their human-readable Unicode form.
unicode_domains = [
    "ドメイン.テスト",        # Japanese: "domain.test"
    "пример.рф",              # Russian: "example.rf"
    "παράδειγμα.δοκιμή",      # Greek: "example.test"
    "例え.テスト",             # Japanese mixed scripts
]

heading("Encoding Unicode domains to ASCII (A-labels)")
note(
    "DNS resolvers only understand ASCII, so each Unicode domain "
    "is encoded into a Punycode form prefixed with <code>xn--</code>."
)

rows = ["<table border='1' cellpadding='6'><tr>"
        "<th>Unicode (U-label)</th><th>ASCII (A-label)</th></tr>"]
for domain in unicode_domains:
    ascii_form = idna.encode(domain).decode("ascii")
    rows.append(f"<tr><td>{domain}</td><td><code>{ascii_form}</code></td></tr>")
rows.append("</table>")
display(HTML("".join(rows)), append=True)

heading("Decoding ASCII domains back to Unicode")
note("Round-tripping through <code>idna.decode</code> recovers the original.")

ascii_input = "xn--eckwd4c7c.xn--zckzah"
recovered = idna.decode(ascii_input)
display(HTML(
    f"<p><code>{ascii_input}</code> &rarr; <strong>{recovered}</strong></p>"
), append=True)

"""
Measuring the *displayed* width of unicode strings.

Python's built-in `len()` counts codepoints, but a terminal cell can be
1 cell wide ('a'), 2 cells wide ('中'), or 0 cells wide (combining
marks like the accent in 'cafe\u0301'). The `wcwidth` package gives
you the real on-screen width.

Docs: https://wcwidth.readthedocs.io/
"""
from IPython.core.display import display, HTML
import wcwidth


heading("len() vs. wcswidth()")
note(
    "Compare Python's <code>len()</code> against "
    "<code>wcwidth.wcswidth()</code> for a few tricky strings."
)

samples = [
    "hello",                 # plain ASCII
    "コンニチハ",              # Japanese, each char is 2 cells
    "cafe\u0301",            # 'café' as 'e' + combining acute (4 codepoints, 4 cells)
    "\U0001F1FF\U0001F1FC",  # 🇿🇼 regional indicator flag (2 codepoints, 2 cells)
    "♀\ufe0f",               # ♀️ with VS-16 (2 codepoints, 2 cells)
]

rows = ["<tr><th>string</th><th>repr</th><th>len()</th><th>wcswidth()</th></tr>"]
for s in samples:
    rows.append(
        f"<tr><td>{s}</td><td><code>{repr(s)}</code></td>"
        f"<td>{len(s)}</td><td>{wcwidth.wcswidth(s)}</td></tr>"
    )
display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

heading("Single-codepoint widths with wcwidth()")
note(
    "<code>wcwidth.wcwidth()</code> returns the width of one codepoint: "
    "0 for combining marks, 1 for narrow, 2 for wide, and -1 for control codes."
)

for ch, label in [
    ("a", "Latin 'a'"),
    ("中", "CJK 'middle'"),
    ("\u0301", "combining acute accent"),
    ("\n", "newline (control code)"),
]:
    note(f"{label} ({repr(ch)}): width = <strong>{wcwidth.wcwidth(ch)}</strong>")

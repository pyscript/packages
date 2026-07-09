"""
A first look at colorama: cross-platform colored terminal text.

Colorama provides three handy namespaces of ANSI escape constants:
`Fore` for foreground color, `Back` for background color, and
`Style` for brightness. Concatenate them with strings, then print
or capture as usual.
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import re
from colorama import Fore, Back, Style


# A tiny helper that converts a string containing colorama's ANSI
# escape sequences into HTML, so we can show "terminal" output in
# the browser. Colorama's job is to produce these escape sequences;
# this helper just renders them visibly here.
_ANSI_TO_CSS = {
    "30": "color:#000", "31": "color:#c33", "32": "color:#3a3",
    "33": "color:#c80", "34": "color:#36c", "35": "color:#a3a",
    "36": "color:#3aa", "37": "color:#ddd", "39": "color:inherit",
    "40": "background:#000", "41": "background:#c33",
    "42": "background:#3a3", "43": "background:#c80",
    "44": "background:#36c", "45": "background:#a3a",
    "46": "background:#3aa", "47": "background:#ddd",
    "49": "background:inherit",
    "1": "font-weight:bold", "2": "opacity:0.6",
    "22": "font-weight:normal;opacity:1",
}

_ANSI_RE = re.compile(r"\x1b\[([0-9;]*)m")


def ansi_to_html(text):
    """Render colorama-styled text as an HTML <pre> block."""
    out = ['<pre style="background:#111;color:#eee;padding:0.7em;'
           'border-radius:6px;font-family:monospace;">']
    open_spans = 0
    pos = 0
    for match in _ANSI_RE.finditer(text):
        out.append(text[pos:match.start()].replace("<", "&lt;"))
        params = match.group(1) or "0"
        if params == "0":
            out.append("</span>" * open_spans)
            open_spans = 0
        else:
            css = ";".join(
                _ANSI_TO_CSS.get(p, "") for p in params.split(";")
            )
            out.append(f'<span style="{css}">')
            open_spans += 1
        pos = match.end()
    out.append(text[pos:].replace("<", "&lt;"))
    out.append("</span>" * open_spans)
    out.append("</pre>")
    return "".join(out)


heading("A colorful greeting")
note(
    "Each colorama constant is just a short ANSI escape string. "
    "Add them to your text, then add Style.RESET_ALL to return "
    "to the terminal's defaults."
)

# Build a styled message. In a real terminal, you'd just print this.
greeting = (
    Fore.GREEN + "Hello"
    + Style.RESET_ALL + ", "
    + Fore.RED + Back.YELLOW + Style.BRIGHT + " world! "
    + Style.RESET_ALL
)

# Show what colorama actually produced (escape codes are visible).
note("The raw string contains ANSI escape sequences:")
display(repr(greeting), append=True)

# Render it as it would appear in a terminal.
note("And here's how a terminal would render it:")
display(HTML(ansi_to_html(greeting)), append=True)

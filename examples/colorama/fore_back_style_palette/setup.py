"""Lighter setup for example 2: same names as cell 1, no IPython shim."""
import re
from pyscript import window, HTML, display as _display
import js

js.alert = window.alert


def display(*args, **kwargs):
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


from colorama import Fore, Back, Style


_ANSI_TO_CSS = {
    "30": "color:#000", "31": "color:#c33", "32": "color:#3a3",
    "33": "color:#c80", "34": "color:#36c", "35": "color:#a3a",
    "36": "color:#3aa", "37": "color:#ddd", "39": "color:inherit",
    "90": "color:#888", "91": "color:#f66", "92": "color:#6f6",
    "93": "color:#ff6", "94": "color:#69f", "95": "color:#f6f",
    "96": "color:#6ff", "97": "color:#fff",
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

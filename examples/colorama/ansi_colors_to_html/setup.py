"""
Shim IPython's display API onto PyScript so example code written in a
Jupyter/IPython idiom runs unmodified in the browser.
"""

import sys
import types
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


ipython = types.ModuleType("IPython")
core = types.ModuleType("IPython.core")
core_display = types.ModuleType("IPython.core.display")
core_display.display = display
core_display.HTML = HTML
ipython.core = core
core.display = core_display
ipython.get_ipython = lambda: None
ipython.display = core_display
sys.modules["IPython"] = ipython
sys.modules["IPython.core"] = core
sys.modules["IPython.core.display"] = core_display
sys.modules["IPython.display"] = core_display


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


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

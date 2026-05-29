"""Shim setup so example code uses IPython idioms in PyScript."""
import sys
import types
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    """Wrap pyscript.display so output lands in the example target."""
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


# Build a minimal IPython package tree and register it in sys.modules
# so the canonical import paths resolve to PyScript's display API.
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
    """Emit an HTML heading so sections are visually separated."""
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    """Emit a short paragraph of explanatory prose."""
    display(HTML(f"<p>{text}</p>"), append=True)


from texttable import Texttable


def show_table(table):
    """Render a Texttable as a monospaced <pre> block."""
    display(HTML(f"<pre>{table.draw()}</pre>"), append=True)

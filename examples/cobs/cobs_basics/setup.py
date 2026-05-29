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
    """Wrap pyscript.display so output lands in the example target."""
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
from cobs import cobs


def hex_view(data, label=None):
    """Render a bytes object as a space-separated hex string."""
    hex_text = " ".join(f"{b:02X}" for b in data)
    prefix = f"<strong>{label}</strong> " if label else ""
    display(
        HTML(
            f"<pre style='font-family:monospace;white-space:pre-wrap'>"
            f"{prefix}({len(data)} bytes)\n{hex_text}</pre>"
        ),
        append=True,
    )

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


import click
from click.testing import CliRunner

# A CliRunner lets us invoke a Click command in-process and capture
# its output, which is perfect for trying things out interactively.
runner = CliRunner()


def show_output(result):
    """Render a CliRunner result as a preformatted block."""
    text = result.output if result.output else "(no output)"
    display(
        HTML(
            f"<pre style='background:#f4f4f4;padding:8px;"
            f"border-radius:4px'>{text}</pre>"
        ),
        append=True,
    )
    note(f"Exit code: <code>{result.exit_code}</code>")

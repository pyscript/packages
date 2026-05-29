"""Lightweight setup for example 2: imports and helpers, no shim."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


import click
from click.testing import CliRunner

runner = CliRunner()


def show_output(result):
    text = result.output if result.output else "(no output)"
    display(
        HTML(
            f"<pre style='background:#f4f4f4;padding:8px;"
            f"border-radius:4px'>{text}</pre>"
        ),
        append=True,
    )
    note(f"Exit code: <code>{result.exit_code}</code>")

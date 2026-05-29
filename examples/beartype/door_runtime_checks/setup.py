"""Lighter setup for example 2. No IPython shim — names below are defined directly."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


from beartype import beartype
from beartype.door import is_bearable, die_if_unbearable
from beartype.roar import BeartypeDoorHintViolation

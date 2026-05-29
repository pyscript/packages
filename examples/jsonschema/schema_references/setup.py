"""Lighter setup for example 3: same names as cell 1, no IPython shim."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


import jsonschema
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

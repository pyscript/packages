"""Setup for the richer-validators example."""
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


import strictyaml
from strictyaml import (
    load, as_document, Map, MapPattern, Seq, FixedSeq, Optional,
    Str, Int, Float, Bool, Decimal, Datetime, Enum, Regex,
    CommaSeparated, EmptyNone, YAMLError,
)

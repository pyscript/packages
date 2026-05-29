"""Setup for the PRecord example. No IPython shim here; the first
example already registered it for the notebook session."""
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


from pyrsistent import (
    PRecord, field, pvector_field, pmap_field,
    InvariantException, PTypeError, v, m, freeze, thaw,
)

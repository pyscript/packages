"""Shim setup for the first example. Includes the full IPython shim."""
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


# pyasn1 imports used by this example.
from pyasn1.type.univ import Integer, Sequence
from pyasn1.type.namedtype import (
    NamedTypes, NamedType, OptionalNamedType, DefaultedNamedType,
)
from pyasn1.type.tag import Tag, tagClassContext, tagFormatSimple
from pyasn1.codec.der.encoder import encode as der_encode
from pyasn1.codec.der.decoder import decode as der_decode


def hexdump(data):
    """Return a space-separated hex string of the bytes in `data`."""
    return " ".join(f"{b:02X}" for b in data)

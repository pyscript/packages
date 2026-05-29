"""Lighter setup: same names as cell 1, no IPython shim."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


from pyasn1.type.univ import Integer, Sequence, SequenceOf
from pyasn1.type.char import UTF8String
from pyasn1.type.namedtype import NamedTypes, NamedType, OptionalNamedType
from pyasn1.codec.der.encoder import encode as der_encode
from pyasn1.codec.der.decoder import decode as der_decode
from pyasn1.codec.native.encoder import encode as to_python
from pyasn1.codec.native.decoder import decode as from_python


def hexdump(data):
    return " ".join(f"{b:02X}" for b in data)

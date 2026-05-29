"""Setup for example 2: same names as cell 1, no IPython shim."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


# Package imports for this example.
import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

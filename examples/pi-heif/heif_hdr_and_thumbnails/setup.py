"""Setup for the third cell: same names as before, no IPython shim."""
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


import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pi_heif
from pi_heif import register_heif_opener, open_heif

register_heif_opener()

"""Setup for the multi-subplot example, back on the html5 canvas backend."""
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


import matplotlib
matplotlib.use("module://matplotlib_pyodide.html5_canvas_backend")

import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

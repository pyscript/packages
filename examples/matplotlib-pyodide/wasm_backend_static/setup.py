"""Setup for the static wasm_backend example. No IPython shim needed."""
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


# This example demonstrates the OTHER backend that matplotlib-pyodide
# ships: wasm_backend, which rasterizes via Agg and shows the result
# as a static image. Selecting it must happen before pyplot import.
import matplotlib
matplotlib.use("module://matplotlib_pyodide.wasm_backend")

import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

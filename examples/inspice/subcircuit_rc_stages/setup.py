"""Setup for the subcircuit example. No IPython shim needed here."""
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
import InSpice
from InSpice import Circuit, SubCircuit, SubCircuitFactory
from InSpice.Unit import u_V, u_Hz, u_Ohm, u_uF, u_kHz, u_kOhm, u_ms

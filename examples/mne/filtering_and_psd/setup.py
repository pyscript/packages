"""Setup for the filtering example. Mirrors the names established in
the first example without re-registering the IPython shim."""

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
import mne

mne.set_log_level("WARNING")
rng = np.random.default_rng(7)

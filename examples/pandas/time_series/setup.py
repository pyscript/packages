"""
Imports and helper functions, for the later pandas examples. Saves having
to repeat this setup code in each example, and also allows us to use a custom
display function that works in the PyScript environment.
"""
import js
from pyscript import window, HTML, display as _display

# Make the standard JavaScript alert function available as js.alert because
# this code is run in a web worker (where alert is not available).
js.alert = window.alert

def display(*args, **kwargs):
  return _display(*args, **kwargs, target=__pyscript_display_target__)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Deterministic randomness so reloads show the same data. Feel free to
# change this seed or remove it to get different data on each reload!
rng = np.random.default_rng(42)

# Helper functions to emit HTML headings and notes, for visual separation
# of sections and to provide explanatory text. You can safely ignore
# these.

def heading(text, level=2):
    # Emit a simple HTML heading so sections are visually separated.
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    # Emit a short paragraph of explanatory prose.
    display(HTML(f"<p>{text}</p>"), append=True)
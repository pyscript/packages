"""Setup for the filtering example."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


import numpy as np
import cv2
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)

"""Lightweight setup for the reaction example (no IPython shim)."""
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
import pandas as pd
import matplotlib.pyplot as plt

from pythermodb_settings.models import Component, Temperature
from pyreactlab_core.models.reaction import Reaction
from pythermocalcdb_nasa import (
    dH_rxn_STD, dS_rxn_STD, dG_rxn_STD, Keq, Keq_vh_shortcut,
)

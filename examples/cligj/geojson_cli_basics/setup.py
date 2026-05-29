"""
Shim IPython's display API onto PyScript so example code written in a
Jupyter/IPython idiom runs unmodified in the browser.
"""

import sys
import types
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    """Wrap pyscript.display so output lands in the example target."""
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


ipython = types.ModuleType("IPython")
core = types.ModuleType("IPython.core")
core_display = types.ModuleType("IPython.core.display")
core_display.display = display
core_display.HTML = HTML
ipython.core = core
core.display = core_display
ipython.get_ipython = lambda: None
ipython.display = core_display
sys.modules["IPython"] = ipython
sys.modules["IPython.core"] = core
sys.modules["IPython.core.display"] = core_display
sys.modules["IPython.display"] = core_display


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


import json
import click
import cligj
from click.testing import CliRunner

# A small synthetic FeatureCollection used as input throughout the
# examples. Three notable points in Europe with a "name" property.
SAMPLE_FEATURES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Eiffel Tower"},
            "geometry": {
                "type": "Point",
                "coordinates": [2.2945, 48.8584],
            },
        },
        {
            "type": "Feature",
            "properties": {"name": "Colosseum"},
            "geometry": {
                "type": "Point",
                "coordinates": [12.4922, 41.8902],
            },
        },
        {
            "type": "Feature",
            "properties": {"name": "Brandenburg Gate"},
            "geometry": {
                "type": "Point",
                "coordinates": [13.3777, 52.5163],
            },
        },
    ],
}

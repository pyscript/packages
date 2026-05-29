"""Lightweight setup for the third cligj example."""
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


import json
import click
import cligj
from click.testing import CliRunner

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

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


# pygame-ce needs a dummy video driver when running headless inside a
# web worker. We must set this BEFORE importing pygame.
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import io
import base64
import pygame


def show_surface(surface, caption=""):
    """Render a pygame Surface as an inline PNG in the page."""
    # pygame.image.save can write to any file-like object. We grab the
    # PNG bytes, base64-encode them, and embed them in an <img> tag.
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, "PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    label = f"<div><em>{caption}</em></div>" if caption else ""
    display(
        HTML(
            f'{label}<img src="data:image/png;base64,{encoded}" '
            f'style="image-rendering: pixelated; max-width: 100%;">'
        ),
        append=True,
    )

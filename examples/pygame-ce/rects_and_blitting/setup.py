"""Setup for the rects-and-blitting example. No IPython shim here."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import io
import base64
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


import pygame
pygame.init()


def show_surface(surface, caption=""):
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

"""Setup for the COBS/R example."""
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


from cobs import cobs, cobsr


def hex_view(data, label=None):
    hex_text = " ".join(f"{b:02X}" for b in data)
    prefix = f"<strong>{label}</strong> " if label else ""
    display(
        HTML(
            f"<pre style='font-family:monospace;white-space:pre-wrap'>"
            f"{prefix}({len(data)} bytes)\n{hex_text}</pre>"
        ),
        append=True,
    )

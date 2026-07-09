"""Lightweight setup for the second example: same names as cell 1, no shim."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


import socket
import asyncio
import matplotlib.pyplot as plt
import aiohappyeyeballs
from aiohappyeyeballs import (
    addr_to_addr_infos,
    pop_addr_infos_interleave,
    remove_addr_infos,
)

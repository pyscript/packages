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


import socket
import aiohappyeyeballs
from aiohappyeyeballs import (
    addr_to_addr_infos,
    pop_addr_infos_interleave,
    remove_addr_infos,
)


def format_addr_infos(addr_infos):
    """Render a list of getaddrinfo-style 5-tuples as an HTML table."""
    rows = ["<tr><th>family</th><th>type</th><th>proto</th><th>address</th></tr>"]
    family_names = {socket.AF_INET: "AF_INET", socket.AF_INET6: "AF_INET6"}
    type_names = {socket.SOCK_STREAM: "SOCK_STREAM", socket.SOCK_DGRAM: "SOCK_DGRAM"}
    for family, type_, proto, _canon, sockaddr in addr_infos:
        rows.append(
            "<tr>"
            f"<td>{family_names.get(family, family)}</td>"
            f"<td>{type_names.get(type_, type_)}</td>"
            f"<td>{proto}</td>"
            f"<td><code>{sockaddr}</code></td>"
            "</tr>"
        )
    table = "<table border='1' cellpadding='4' cellspacing='0'>" + "".join(rows) + "</table>"
    display(HTML(table), append=True)

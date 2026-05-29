"""
A first look at `distro`: querying basic OS distribution info.

`distro` reads OS-release files (and similar sources) to give you a
reliable, machine-readable picture of the system Python is running on.
It's the modern replacement for the removed `platform.linux_distribution`.

Docs: https://distro.readthedocs.io/
"""
from IPython.core.display import display, HTML

heading("Who am I running on?")
note(
    "The most common starting point: a friendly name, a stable ID, "
    "and a version string."
)

# `name(pretty=True)` returns a human-readable label like
# "Ubuntu 22.04.3 LTS (Jammy Jellyfish)". Without `pretty`, it returns
# just the distribution's name.
display(HTML(
    f"<ul>"
    f"<li><b>Pretty name:</b> {distro.name(pretty=True) or '(unknown)'}</li>"
    f"<li><b>Plain name:</b> {distro.name() or '(unknown)'}</li>"
    f"<li><b>ID:</b> <code>{distro.id() or '(unknown)'}</code></li>"
    f"<li><b>Version:</b> {distro.version(best=True) or '(unknown)'}</li>"
    f"<li><b>Codename:</b> {distro.codename() or '(none)'}</li>"
    f"</ul>"
), append=True)

note(
    "Inside the Pyodide sandbox there's no traditional Linux "
    "distribution to detect, so several of these fields may come "
    "back empty. On a real Linux host you would see values like "
    "<code>id() == 'ubuntu'</code> or <code>id() == 'fedora'</code>."
)

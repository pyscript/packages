"""
A first look at matplotlib-pyodide.

This package provides two HTML5 backends for matplotlib that work
inside Pyodide:

  - module://matplotlib_pyodide.wasm_backend
        Renders the Agg buffer to a static <canvas>.
  - module://matplotlib_pyodide.html5_canvas_backend
        Draws directly to an HTML5 <canvas> with native fonts and
        crisp vector strokes; supports interactivity.

You select a backend with matplotlib.use(...), exactly as you would
on the desktop. See:
    https://github.com/pyodide/matplotlib-pyodide

For this example, the html5_canvas_backend has already been activated
in setup.py before pyplot was imported.
"""
from IPython.core.display import display, HTML

heading("matplotlib-pyodide: an interactive canvas plot")
note(
    "We're rendering through the <code>html5_canvas_backend</code>, "
    "which draws to a real HTML5 canvas instead of producing a PNG. "
    "Text uses the browser's fonts and lines stay sharp on zoom."
)

# Confirm the active backend at runtime.
import matplotlib
note(f"Active matplotlib backend: <code>{matplotlib.get_backend()}</code>")

# A small synthetic signal: a damped oscillation. The kind of plot
# you'd reach for when sanity-checking a model in a notebook.
t = np.linspace(0, 6 * np.pi, 400)
signal = np.exp(-t / 8) * np.sin(t)
envelope = np.exp(-t / 8)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(t, signal, color="navy", linewidth=2, label="damped sine")
ax.plot(t, envelope, color="crimson", linestyle="--",
        linewidth=1, label="envelope")
ax.plot(t, -envelope, color="crimson", linestyle="--", linewidth=1)
ax.axhline(0, color="gray", linewidth=0.5)
ax.set_title("A damped oscillation, drawn on an HTML5 canvas")
ax.set_xlabel("time")
ax.set_ylabel("amplitude")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)

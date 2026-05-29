"""Shim IPython's display API onto PyScript and import altair."""
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


import altair as alt
import pandas as pd


def show_chart(chart):
    """Render an Altair chart as inline HTML via Vega-Embed."""
    spec = chart.to_json()
    html = f"""
    <div class="altair-chart"></div>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    <script type="application/json" class="vega-spec">{spec}</script>
    <script>
      (function() {{
        var scripts = document.getElementsByClassName('vega-spec');
        var el = scripts[scripts.length - 1];
        var spec = JSON.parse(el.textContent);
        var target = el.previousElementSibling;
        function embed() {{
          if (window.vegaEmbed) {{
            vegaEmbed(target, spec, {{actions: false}});
          }} else {{
            setTimeout(embed, 100);
          }}
        }}
        embed();
      }})();
    </script>
    """
    display(HTML(html), append=True)

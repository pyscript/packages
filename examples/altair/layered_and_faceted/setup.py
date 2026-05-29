"""Imports and helpers for the second altair example."""
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(*args, **kwargs, target=__pyscript_display_target__)


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)


import altair as alt
import pandas as pd
import numpy as np

rng = np.random.default_rng(7)


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

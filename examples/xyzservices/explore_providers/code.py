"""
A first look at xyzservices.

xyzservices is a lightweight catalog of XYZ raster tile providers
(the basemaps you see behind interactive maps). It ships a single
JSON database and a Python API for browsing and using each provider.

Docs: https://xyzservices.readthedocs.io/
"""
from IPython.core.display import display, HTML

import xyzservices
import xyzservices.providers as xyz


heading("Browsing the provider catalog")
note(
    "The <code>xyzservices.providers</code> module is a "
    "<code>Bunch</code> (an enhanced dict) of tile providers. "
    "Top-level keys are families like CartoDB, OpenStreetMap, "
    "Esri, and so on."
)

# Top-level provider families. Many entries are themselves Bunches
# containing several variants (e.g., CartoDB.Positron, CartoDB.Voyager).
families = sorted(xyz.keys())
note(f"There are <strong>{len(families)}</strong> provider families. "
     f"A sample: {', '.join(families[:8])}, ...")

# Pick a single, free, no-token-needed provider to inspect.
positron = xyz.CartoDB.Positron

note("A <code>TileProvider</code> is a dict-like object with the "
     "metadata you need to actually request tiles:")
display(HTML(
    f"<ul>"
    f"<li><b>name:</b> {positron.name}</li>"
    f"<li><b>url template:</b> <code>{positron.url}</code></li>"
    f"<li><b>attribution:</b> {positron.html_attribution}</li>"
    f"<li><b>max zoom:</b> {positron.max_zoom}</li>"
    f"</ul>"
), append=True)

heading("Building a real tile URL", level=3)
note(
    "The <code>build_url</code> method fills in the "
    "<code>{x}</code>, <code>{y}</code>, <code>{z}</code> and any "
    "provider-specific placeholders (like <code>{variant}</code> "
    "or <code>{r}</code> for retina)."
)

# Tile coordinates for roughly central London at zoom 6.
tile_url = positron.build_url(x=32, y=21, z=6)
display(HTML(f"<code>{tile_url}</code>"), append=True)

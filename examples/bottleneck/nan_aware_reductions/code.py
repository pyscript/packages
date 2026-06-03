"""
A first look at Bottleneck: fast NumPy array functions written in C.

Bottleneck shines on arrays that contain NaN ("not a number") values --
the kind of gaps you get from missing sensor readings or unanswered
survey questions. Its `nan*` functions skip the gaps for you, faster
than NumPy's equivalents.

Docs: https://bottleneck.readthedocs.io
Source: https://github.com/pydata/bottleneck
"""
from IPython.core.display import display, HTML

import numpy as np
import bottleneck as bn

rng = np.random.default_rng(42)


# Imagine an array of daily rainfall (mm) for a weather station, with
# NaN marking days when the rain gauge was offline.
rainfall = np.array(
    [2.1, 0.0, np.nan, 5.3, 1.2, np.nan, 0.4, 8.9, 0.0, 3.7]
)

heading("A small array with missing readings")
note(
    "Some entries are NaN. NumPy's plain `mean` would propagate "
    "NaN through the result; Bottleneck's `nanmean` skips them."
)
display(rainfall, append=True)

# Compare NumPy and Bottleneck side by side.
note(f"<code>np.mean(rainfall)</code> = {np.mean(rainfall)}")
note(f"<code>bn.nanmean(rainfall)</code> = {bn.nanmean(rainfall):.3f}")

# Bottleneck offers the full family of NaN-aware reductions.
heading("Reductions that ignore NaN")
summary = {
    "nansum":    bn.nansum(rainfall),
    "nanmean":   bn.nanmean(rainfall),
    "nanstd":    bn.nanstd(rainfall),
    "nanmin":    bn.nanmin(rainfall),
    "nanmax":    bn.nanmax(rainfall),
    "nanmedian": bn.nanmedian(rainfall),
}
for name, value in summary.items():
    note(f"<code>bn.{name}</code> &rarr; {value:.3f}")

# `nanargmin` / `nanargmax` give you the position of the extreme,
# again ignoring NaN.
wettest_day = bn.nanargmax(rainfall)
note(
    f"Wettest recorded day was index <strong>{wettest_day}</strong> "
    f"with {rainfall[wettest_day]} mm."
)

# Quick sanity checks that come up constantly when cleaning data.
heading("Quick checks")
note(f"<code>bn.anynan(rainfall)</code> &rarr; {bn.anynan(rainfall)}")
note(f"<code>bn.allnan(rainfall)</code> &rarr; {bn.allnan(rainfall)}")

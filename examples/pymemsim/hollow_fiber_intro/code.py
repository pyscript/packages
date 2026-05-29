"""
A first look at PyMemSim.

PyMemSim simulates membrane-based separation systems. Its current focus
is the hollow-fiber membrane (HFM) module: long, thin fibers across
which gas or liquid components selectively permeate, separating a feed
mixture into a retentate and a permeate stream.

This first example simply explores what the package exposes, so we know
what to reach for next. See:
    https://github.com/sinagilassi/PyMemSim
"""
from IPython.core.display import display, HTML

heading("PyMemSim version")
note(f"Running PyMemSim <strong>{pms.__version__}</strong> in your browser.")

# The package's public surface is small and discoverable. The two names
# you'll use most often are HFM (the hollow-fiber membrane interface)
# and create_hfm_module (a factory that wires options + inputs into a
# ready-to-simulate module).
heading("Top-level names worth knowing")
public_names = [name for name in dir(pms) if not name.startswith("_")]
note("Public attributes exposed by <code>pymemsim</code>:")
display(HTML("<pre>" + ", ".join(public_names) + "</pre>"), append=True)

# A quick sketch of the conceptual setup, so the next example feels
# familiar before we dive into solver details.
heading("The hollow-fiber picture")
note(
    "Imagine a bundle of porous fibers in a shell. A feed mixture "
    "enters one side; some components permeate through the fiber "
    "walls more readily than others. Two flow arrangements are "
    "supported:"
)
display(HTML(
    "<ul>"
    "<li><strong>Co-current</strong>: feed and permeate flow in the "
    "same direction. Solved as an initial-value problem.</li>"
    "<li><strong>Counter-current</strong>: feed and permeate flow in "
    "opposite directions. Solved as a boundary-value problem.</li>"
    "</ul>"
), append=True)

# A tiny illustrative sketch of what selective permeation looks like
# along a fiber: the more-permeable component drops faster on the
# feed side, while the permeate side becomes enriched in it.
heading("Sketch: composition along a fiber")
length_fraction = np.linspace(0, 1, 60)
feed_fast = 0.50 * np.exp(-2.5 * length_fraction)        # e.g. CO2
feed_slow = 0.50 * np.exp(-0.4 * length_fraction)        # e.g. N2
permeate_fast = 1 - feed_fast / feed_fast[0] * 0.55      # enriched
permeate_slow = 1 - permeate_fast

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(length_fraction, feed_fast, label="Feed: fast component", color="crimson")
ax.plot(length_fraction, feed_slow, label="Feed: slow component", color="navy")
ax.plot(length_fraction, permeate_fast, "--", label="Permeate: fast", color="crimson")
ax.plot(length_fraction, permeate_slow, "--", label="Permeate: slow", color="navy")
ax.set_xlabel("Fractional length along fiber")
ax.set_ylabel("Mole fraction (illustrative)")
ax.set_title("Selective permeation along a hollow fiber")
ax.legend()
fig.tight_layout()
display(fig, append=True)

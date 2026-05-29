"""
Getting started with contourpy.

contourpy computes contours of 2D quadrilateral grids. It's the engine
behind Matplotlib's contour functions, but you can use it directly to
get raw line geometry as NumPy arrays -- handy when you want to do
something with contours other than draw them.

Docs: https://contourpy.readthedocs.io
"""
from IPython.core.display import display, HTML

# A smooth scalar field on a 60x60 grid: imagine elevation in metres
# above sea level over a small patch of countryside.
grid_x, grid_y = np.meshgrid(
    np.linspace(-3, 3, 60),
    np.linspace(-3, 3, 60),
)
elevation = (
    3 * np.exp(-((grid_x - 0.5) ** 2 + (grid_y - 0.5) ** 2))
    - 2 * np.exp(-((grid_x + 1.2) ** 2 + (grid_y + 0.8) ** 2) / 0.6)
    + 0.4 * grid_x
)

heading("1. A contour generator and a single level")
note(
    "Pass x, y, and z arrays to <code>contour_generator</code>. "
    "It returns an object you can query for contour lines at any "
    "z-level. Each line is a NumPy array of (x, y) points."
)

cont_gen = contour_generator(x=grid_x, y=grid_y, z=elevation)

# A single z-level: the 1.0 m elevation contour.
contour_lines_at_one = cont_gen.lines(1.0)
note(
    f"At z=1.0 there are <strong>{len(contour_lines_at_one)}</strong> "
    f"separate contour line(s). The first has shape "
    f"<code>{contour_lines_at_one[0].shape}</code>."
)

heading("2. Multiple levels at once with multi_lines")
note(
    "<code>multi_lines</code> returns a list of line lists, one per "
    "requested level. Here we ask for five evenly spaced levels."
)

levels = np.linspace(elevation.min() + 0.2, elevation.max() - 0.2, 5)
multi_lines = cont_gen.multi_lines(levels.tolist())

fig, ax = plt.subplots(figsize=(6, 5))
# Faint background showing the underlying field.
ax.imshow(
    elevation,
    extent=(grid_x.min(), grid_x.max(), grid_y.min(), grid_y.max()),
    origin="lower", cmap="terrain", alpha=0.6,
)
# Draw each level's lines in its own colour.
colours = plt.cm.viridis(np.linspace(0, 1, len(levels)))
for level_value, lines_at_level, colour in zip(levels, multi_lines, colours):
    for line in lines_at_level:
        ax.plot(line[:, 0], line[:, 1], color=colour, linewidth=1.5,
                label=f"z={level_value:.2f}")

# Deduplicate legend entries (one per level).
handles, labels = ax.get_legend_handles_labels()
seen = {}
for handle, label in zip(handles, labels):
    seen.setdefault(label, handle)
ax.legend(seen.values(), seen.keys(), loc="upper left", fontsize=8)
ax.set_title("Contour lines computed by contourpy")
ax.set_xlabel("x")
ax.set_ylabel("y")
fig.tight_layout()
display(fig, append=True)

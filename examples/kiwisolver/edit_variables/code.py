# ---------------------------------------------------------------------
# Edit variables: re-solving as one input changes.
# ---------------------------------------------------------------------
#
# A common pattern is to build the constraint system once and then
# nudge a single value (a window width, a slider, a mouse position)
# and let the solver propagate the change. That's what edit variables
# are for.

heading("A resizable three-pane layout")
note(
    "Three side-by-side panes: a fixed 80px sidebar on the left, "
    "a flexible main pane, and a 120px-minimum inspector on the right. "
    "We'll vary the total width and watch the panes adjust."
)

sidebar_l = kiwi.Variable("sidebar_l")
sidebar_r = kiwi.Variable("sidebar_r")
main_l = kiwi.Variable("main_l")
main_r = kiwi.Variable("main_r")
inspect_l = kiwi.Variable("inspect_l")
inspect_r = kiwi.Variable("inspect_r")
total_width = kiwi.Variable("total_width")

solver = kiwi.Solver()

# Required structural constraints: panes meet edge to edge, starting
# at 0.
for c in [
    sidebar_l == 0,
    main_l == sidebar_r,
    inspect_l == main_r,
    inspect_r == total_width,
    (sidebar_r - sidebar_l) == 80,           # fixed sidebar width
    (inspect_r - inspect_l) >= 120,          # inspector minimum
    (main_r - main_l) >= 100,                # main pane minimum
]:
    solver.addConstraint(c)

# Prefer the inspector to stay near 160 px (a soft preference).
solver.addConstraint(((inspect_r - inspect_l) == 160) | "weak")

# Register total_width as an edit variable so we can change it
# repeatedly without rebuilding the system.
solver.addEditVariable(total_width, "strong")

widths_to_try = [400, 600, 800, 1000, 1200]
rows = []
for w in widths_to_try:
    solver.suggestValue(total_width, w)
    solver.updateVariables()
    rows.append((
        w,
        sidebar_r.value() - sidebar_l.value(),
        main_r.value() - main_l.value(),
        inspect_r.value() - inspect_l.value(),
    ))

# Show the numbers, then draw the layouts stacked on top of each other.
table = "<table border='1' cellpadding='4' style='border-collapse:collapse'>"
table += "<tr><th>total</th><th>sidebar</th><th>main</th><th>inspector</th></tr>"
for total, s, m, i in rows:
    table += (
        f"<tr><td>{total}</td><td>{s:.0f}</td>"
        f"<td>{m:.0f}</td><td>{i:.0f}</td></tr>"
    )
table += "</table>"
display(HTML(table), append=True)

fig, ax = plt.subplots(figsize=(9, 3.5))
colors = {"sidebar": "#88aaff", "main": "#ffd28a", "inspector": "#a8e6a3"}
for row_index, (total, s, m, i) in enumerate(rows):
    y = row_index
    ax.barh(y, s, left=0, color=colors["sidebar"], edgecolor="black")
    ax.barh(y, m, left=s, color=colors["main"], edgecolor="black")
    ax.barh(y, i, left=s + m, color=colors["inspector"], edgecolor="black")
    ax.text(s / 2, y, "side", ha="center", va="center", fontsize=8)
    ax.text(s + m / 2, y, "main", ha="center", va="center", fontsize=8)
    ax.text(s + m + i / 2, y, "inspector",
            ha="center", va="center", fontsize=8)

ax.set_yticks(range(len(rows)))
ax.set_yticklabels([f"{r[0]} px" for r in rows])
ax.set_xlabel("Pixels")
ax.set_title("Three-pane layout solved at five total widths")
ax.invert_yaxis()
fig.tight_layout()
display(fig, append=True)

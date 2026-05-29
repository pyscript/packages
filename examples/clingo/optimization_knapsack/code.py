# ---------------------------------------------------------------------
# Optimization: clingo isn't just for satisfaction problems. With
# `#minimize` / `#maximize` statements it returns optimal answer sets.
# Here we solve a small 0/1 knapsack: pick items to maximize value
# while staying under a weight limit.
# ---------------------------------------------------------------------

heading("Packing a hiker's backpack")
note(
    "Eight items, each with a weight and a value. The pack holds at "
    "most 15 kg. We want the most valuable selection that fits. "
    "<code>#maximize</code> tells clingo which models to prefer."
)

items = [
    # (name, weight_kg, value)
    ("tent",       4, 10),
    ("sleepingbag", 3, 8),
    ("stove",      2, 6),
    ("food",       5, 12),
    ("water",      4, 9),
    ("camera",     1, 5),
    ("book",       1, 2),
    ("firstaid",   2, 7),
]
capacity = 15

# Encode items as facts and let clingo choose which to take.
item_facts = "\n".join(
    f"item({name},{w},{v})." for name, w, v in items
)

program = f"""
{item_facts}

% Choose any subset of items.
{{ take(I) : item(I, _, _) }}.

% Total weight must not exceed capacity.
:- #sum {{ W,I : take(I), item(I, W, _) }} > {capacity}.

% Maximize total value across chosen items.
#maximize {{ V,I : take(I), item(I, _, V) }}.

#show take/1.
"""

control = Control(["--opt-mode=opt"])  # find provably optimal model
control.add("base", [], program)
control.ground([("base", [])])

best = {"items": [], "cost": None}

def on_model(model):
    # Each model improves on the previous; the last one is optimal.
    chosen = [a.arguments[0].name for a in model.symbols(shown=True)]
    best["items"] = chosen
    best["cost"] = model.cost  # list of optimization values

result = control.solve(on_model=on_model)

note(f"Solver result: <code>{result}</code> "
     f"(<code>SAT</code> with optimum proven).")

# Summarize the chosen pack.
weight_lookup = {n: (w, v) for n, w, v in items}
chosen_rows = []
total_w = 0
total_v = 0
for name in best["items"]:
    w, v = weight_lookup[name]
    total_w += w
    total_v += v
    chosen_rows.append(
        f"<tr><td>{name}</td><td>{w} kg</td><td>{v}</td></tr>"
    )

table = (
    "<table style='border-collapse:collapse;'>"
    "<tr><th style='text-align:left;padding:4px 10px;'>Item</th>"
    "<th style='padding:4px 10px;'>Weight</th>"
    "<th style='padding:4px 10px;'>Value</th></tr>"
    + "".join(chosen_rows)
    + f"<tr style='font-weight:bold;border-top:1px solid #999;'>"
    f"<td style='padding:4px 10px;'>Total</td>"
    f"<td style='padding:4px 10px;'>{total_w} kg</td>"
    f"<td style='padding:4px 10px;'>{total_v}</td></tr>"
    "</table>"
)
display(HTML(table), append=True)

note(
    f"Clingo's reported optimization cost: <code>{best['cost']}</code>. "
    "Negative because <code>#maximize V</code> is internally encoded "
    "as <code>#minimize -V</code>."
)

"""
A first taste of cytoolz: slicing and summarizing iterables.

cytoolz functions return iterators wherever possible, so they compose
cheaply over very large (even infinite) sequences. We materialize them
with `list()` only when we want to look at the result.
"""
from IPython.core.display import display, HTML

# A small stream of orders from a fictional online tea shop. Each order
# is a dict; we'll slice it, summarize it, and group it.
orders = [
    {"id": 1, "tea": "earl grey",   "qty": 2, "country": "UK"},
    {"id": 2, "tea": "matcha",      "qty": 1, "country": "JP"},
    {"id": 3, "tea": "rooibos",     "qty": 4, "country": "ZA"},
    {"id": 4, "tea": "earl grey",   "qty": 1, "country": "UK"},
    {"id": 5, "tea": "matcha",      "qty": 3, "country": "JP"},
    {"id": 6, "tea": "oolong",      "qty": 2, "country": "TW"},
    {"id": 7, "tea": "earl grey",   "qty": 5, "country": "US"},
    {"id": 8, "tea": "rooibos",     "qty": 1, "country": "ZA"},
    {"id": 9, "tea": "matcha",      "qty": 2, "country": "JP"},
]

heading("1. Slicing iterables: take, drop, partition")
note(
    "These return iterators, so we wrap them in <code>list</code> "
    "to inspect them."
)

display({"first 3 orders": list(take(3, orders))}, append=True)
display({"after first 3":  list(drop(3, orders))}, append=True)

# Partition into fixed-size chunks. `partition_all` keeps any
# trailing remainder, while `partition` would drop it.
chunks = list(partition_all(4, orders))
note(f"Partitioned into {len(chunks)} chunks of up to 4:")
display(chunks, append=True)

heading("2. Plucking and counting")
note(
    "<code>pluck</code> grabs a key from each dict; "
    "<code>frequencies</code> counts occurrences."
)

teas = list(pluck("tea", orders))
display({"teas in order": teas}, append=True)
display({"frequencies": frequencies(teas)}, append=True)

heading("3. Grouping records by a key")
note(
    "<code>groupby</code> takes a key function (or a string key, "
    "for dicts) and returns a plain <code>dict</code>."
)

by_country = groupby("country", orders)
for country, rows in by_country.items():
    note(f"<strong>{country}</strong>: {len(rows)} order(s)")
    display(rows, append=True)

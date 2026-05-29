"""
A first taste of `toolz`: tools for iterables.

`toolz` is a small, dependency-free library of functional helpers
inspired by Clojure and the Python standard library's `itertools`
and `functools`. Docs: https://toolz.readthedocs.io
"""
from IPython.core.display import display, HTML
from toolz import groupby, frequencies, partition, unique, take, concat

# A small log of recent orders from a fictional coffee shop.
orders = [
    {"customer": "Ada",   "drink": "latte",      "price": 4.50},
    {"customer": "Ben",   "drink": "espresso",   "price": 3.00},
    {"customer": "Ada",   "drink": "cappuccino", "price": 4.25},
    {"customer": "Cleo",  "drink": "latte",      "price": 4.50},
    {"customer": "Ben",   "drink": "latte",      "price": 4.50},
    {"customer": "Cleo",  "drink": "espresso",   "price": 3.00},
    {"customer": "Ada",   "drink": "latte",      "price": 4.50},
    {"customer": "Dax",   "drink": "mocha",      "price": 5.00},
    {"customer": "Ben",   "drink": "mocha",      "price": 5.00},
]

heading("groupby: bucket items by a key")
note(
    "Pass a key function (or a string key) and an iterable. "
    "You get back a dict of lists."
)
by_customer = groupby("customer", orders)
for name, items in by_customer.items():
    drinks = ", ".join(o["drink"] for o in items)
    note(f"<strong>{name}</strong>: {drinks}")

heading("frequencies: count occurrences")
drink_counts = frequencies(o["drink"] for o in orders)
display(drink_counts, append=True)

heading("unique: keep first sighting, preserve order")
seen_customers = list(unique(o["customer"] for o in orders))
display(seen_customers, append=True)

heading("partition + take: chunk and peek")
note("Split into pairs of consecutive prices, then take the first three pairs.")
prices = [o["price"] for o in orders]
pairs = list(take(3, partition(2, prices)))
display(pairs, append=True)

heading("concat: flatten one level of nesting")
nested = [[1, 2], [3, 4], [5]]
display(list(concat(nested)), append=True)

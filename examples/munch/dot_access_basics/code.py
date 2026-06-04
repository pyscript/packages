"""
Getting started with Munch: a dict that you can also poke at with dots.

A Munch behaves exactly like a regular dictionary, but its keys can be
accessed (and assigned) as attributes. Handy for config objects, parsed
JSON, or anything where `config["database"]["host"]` starts to feel
clunky compared to `config.database.host`.

Docs and source: https://github.com/Infinidat/munch
"""

from IPython.core.display import display, HTML

# Package imports for this example.
from munch import Munch, munchify, unmunchify


heading("1. A Munch is just a dict with attribute access")
note(
    "Build a small profile for an imaginary coffee-shop customer. "
    "Notice how we can mix bracket-style and dot-style access freely."
)

customer = Munch()
customer.name = "Ada Lovelace"
customer.favorite_drink = "flat white"
customer["loyalty_points"] = 142

note(f"customer.name &rarr; <strong>{customer.name}</strong>")
note(f'customer["favorite_drink"] &rarr; <strong>{customer["favorite_drink"]}</strong>')
note(f"customer.loyalty_points &rarr; <strong>{customer.loyalty_points}</strong>")

# Munch is a real dict subclass, so all the usual methods work.
note(f"Keys: {list(customer.keys())}")
note(f"isinstance(customer, dict) &rarr; {isinstance(customer, dict)}")

heading("2. Nesting works naturally")
note(
    "Assign a Munch as a value and you can chain dot access all the "
    "way down."
)

customer.address = Munch(city="London", postcode="EC1A 1BB")
note(f"customer.address.city &rarr; <strong>{customer.address.city}</strong>")
note(f"customer.address.postcode &rarr; <strong>{customer.address.postcode}</strong>")

heading("3. Convert to/from plain dicts with munchify / unmunchify")
note(
    "Got a nested dict from somewhere (parsed JSON, a config file)? "
    "Pass it through munchify and the whole tree becomes dot-accessible."
)

raw_order = {
    "order_id": "A-1042",
    "line_items": [          # renamed from "items"
        {"name": "croissant", "qty": 2},
        {"name": "flat white", "qty": 1},
    ],
    "totals": {"subtotal": 8.50, "tax": 0.68},
}

order = munchify(raw_order)
note(f"order.order_id &rarr; <strong>{order.order_id}</strong>")
note(f"order.line_items[0].name &rarr; <strong>{order.line_items[0].name}</strong>")
note(f"order.totals.subtotal &rarr; <strong>{order.totals.subtotal}</strong>")

# Going back is just as easy.
plain = unmunchify(order)
note(f"unmunchify gives back a plain dict: {type(plain).__name__}")
display(plain, append=True)

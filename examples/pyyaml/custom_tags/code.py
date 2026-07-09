# ---------------------------------------------------------------------
# YAML's tag system lets you add types of your own. Here we teach
# PyYAML how to read and write a domain-specific "!money" tag, which
# is handy for fixtures, configs, and test data.
# ---------------------------------------------------------------------

heading("Custom tags: a !money type")
note(
    "We define a small <code>Money</code> class, register a "
    "<em>constructor</em> so PyYAML can build it from a "
    "<code>!money</code> scalar like <code>!money 19.99 USD</code>, "
    "and a <em>representer</em> so dumping a <code>Money</code> "
    "instance produces the same compact form."
)


class Money:
    """A simple amount-and-currency value."""

    def __init__(self, amount, currency):
        self.amount = float(amount)
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount:.2f}, {self.currency!r})"


def money_constructor(loader, node):
    """Turn a YAML scalar like '19.99 USD' into a Money object."""
    text = loader.construct_scalar(node)
    amount_str, currency = text.split()
    return Money(amount_str, currency)


def money_representer(dumper, data):
    """Turn a Money object back into a !money scalar."""
    return dumper.represent_scalar(
        "!money", f"{data.amount:.2f} {data.currency}",
    )


# Register with the safe loader/dumper so we keep using safe_load /
# safe_dump and don't open the door to arbitrary Python objects.
yaml.SafeLoader.add_constructor("!money", money_constructor)
yaml.SafeDumper.add_representer(Money, money_representer)

cart_yaml = """
customer: Ada Lovelace
items:
  - name: Notebook
    price: !money 12.50 USD
  - name: Fountain pen
    price: !money 48.00 USD
  - name: Ink (bottle)
    price: !money 9.95 USD
"""

cart = yaml.safe_load(cart_yaml)

note("Parsed cart with <code>Money</code> objects in place of strings:")
for item in cart["items"]:
    price = item["price"]
    note(
        f"&bull; <strong>{item['name']}</strong> &mdash; "
        f"{price.amount:.2f} {price.currency}"
    )

total = sum(item["price"].amount for item in cart["items"])
cart["total"] = Money(total, "USD")

heading("Round-tripping back to YAML")
note(
    "Dumping the updated cart shows our representer in action: the "
    "<code>total</code> field comes out with the same <code>!money</code> "
    "tag we started with."
)

out = yaml.safe_dump(cart, default_flow_style=False, sort_keys=False)
display(HTML(f"<pre>{out}</pre>"), append=True)

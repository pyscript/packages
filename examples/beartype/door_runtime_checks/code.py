# ---------------------------------------------------------------------
# Beartype's DOOR (Decidedly Object-Oriented Runtime-checking) API lets
# you check arbitrary objects against arbitrary type hints — anywhere,
# anytime, no decorator required.
# ---------------------------------------------------------------------
from beartype import beartype
from beartype.door import is_bearable, die_if_unbearable
from beartype.roar import BeartypeDoorHintViolation


heading("1. is_bearable: a turbocharged isinstance")
note(
    "Use is_bearable(obj, hint) like isinstance, but with full type hint "
    "syntax — including parameterized generics like list[str]."
)

shopping_list = ["bread", "milk", "eggs"]
mixed_bag = ["bread", 42, "eggs"]

display(
    {
        "is shopping_list a list[str]?": is_bearable(shopping_list, list[str]),
        "is mixed_bag a list[str]?": is_bearable(mixed_bag, list[str]),
        "is mixed_bag a list[str | int]?": is_bearable(mixed_bag, list[str | int]),
    },
    append=True,
)


heading("2. die_if_unbearable: assertion-style guarding")
note(
    "die_if_unbearable raises BeartypeDoorHintViolation when the object "
    "fails its hint. Use it as a sharp-edged precondition check."
)

# A nested hint: a dict mapping product names to (quantity, price) pairs.
Inventory = dict[str, tuple[int, float]]

good_inventory = {"apple": (10, 0.50), "pear": (4, 0.75)}
bad_inventory = {"apple": (10, 0.50), "pear": (4, "free")}  # price is wrong

die_if_unbearable(good_inventory, Inventory)
note("The good inventory passed silently. Now we'll try the bad one:")

try:
    die_if_unbearable(bad_inventory, Inventory)
except BeartypeDoorHintViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)


heading("3. Combining @beartype with nested hints")
note(
    "The same hint vocabulary works inside @beartype-decorated functions. "
    "Here we accept any mapping of orders and return a per-customer total."
)

@beartype
def total_by_customer(
    orders: list[tuple[str, float]],
) -> dict[str, float]:
    totals: dict[str, float] = {}
    for customer, amount in orders:
        totals[customer] = round(totals.get(customer, 0.0) + amount, 2)
    return totals

orders = [
    ("Ada", 12.50),
    ("Grace", 7.25),
    ("Ada", 3.00),
    ("Grace", 9.75),
]
display(total_by_customer(orders), append=True)

"""
A first look at pyrsistent: persistent (immutable) collections.

Every "mutating" operation returns a new structure and leaves the
original untouched. Behind the scenes the new and old versions share
most of their data, so this is fast and memory-efficient.

Docs: https://pyrsistent.readthedocs.org/
"""
from IPython.core.display import display, HTML
# Pyrsistent provides immutable, "persistent" data structures inspired
# by Clojure. We import the most common building blocks here.
from pyrsistent import v, m, pmap, s, freeze, thaw


heading("1. PVector: an immutable list")
note(
    "We start with a small shopping list. Each 'change' returns a "
    "brand-new vector; the originals never change."
)

shopping = v("apples", "bread", "cheese")
with_eggs = shopping.append("eggs")
swapped = with_eggs.set(1, "sourdough")

note(f"Original:    {shopping}")
note(f"After append: {with_eggs}")
note(f"After set(1): {swapped}")
note(f"shopping is unchanged: {shopping == v('apples', 'bread', 'cheese')}")

# PVector supports the full Sequence protocol: indexing, slicing,
# iteration, len, etc.
note(f"swapped[1:3] = {swapped[1:3]}, len = {len(swapped)}")

heading("2. PMap: an immutable dict")
note(
    "A tiny inventory keyed by SKU. We 'evolve' the map by setting "
    "and updating; the original map keeps its values."
)

inventory = m(apples=12, bread=4, cheese=7)
restocked = inventory.set("bread", 20)
combined = restocked.update(m(eggs=18, cheese=10))

note(f"Original:  {inventory}")
note(f"Restocked: {restocked}")
note(f"Combined:  {combined}")

# PMaps are hashable, so they can be used as dict keys or set members,
# unlike Python's built-in dict.
warehouse = pmap({combined: "Warehouse A", inventory: "Warehouse B"})
note(f"PMaps as keys works: {len(warehouse)} warehouses indexed.")

heading("3. PSet and freeze/thaw")
note(
    "freeze() recursively converts plain Python containers into "
    "pyrsistent ones; thaw() converts back."
)

tags = s("fresh", "local", "fresh")  # duplicates collapse, like set
note(f"PSet (duplicates dropped): {tags}")

raw = {"name": "Market", "items": [{"sku": "A1", "qty": 3}]}
frozen = freeze(raw)
note(f"Frozen: {frozen}")
note(f"Type of inner list: {type(frozen['items']).__name__}")
note(f"Thawed back to plain Python: {thaw(frozen)}")

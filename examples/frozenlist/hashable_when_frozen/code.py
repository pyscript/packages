# ---------------------------------------------------------------------
# Frozen FrozenLists are hashable, so they can be dict keys or set
# members. Unfrozen ones are not -- hashing them raises RuntimeError.
# ---------------------------------------------------------------------

heading("Why hashability matters")
note(
    "Imagine tagging recipes by their ingredient lists. If the "
    "ingredient list is a regular Python list, you can't use it "
    "as a dict key. A frozen FrozenList works as a key, because "
    "freezing makes it hashable."
)

# A few recipes, each described by an ordered ingredient list.
raw_recipes = {
    "Margherita pizza": ["flour", "tomato", "mozzarella", "basil"],
    "Caprese salad":    ["tomato", "mozzarella", "basil"],
    "Tomato bruschetta":["bread", "tomato", "basil", "olive oil"],
    "Cheese toastie":   ["bread", "mozzarella"],
}


def freeze_ingredients(items):
    """Build a FrozenList from items and freeze it before returning."""
    fl = FrozenList(items)
    fl.freeze()
    return fl


# Try hashing an unfrozen list to show it fails.
unfrozen = FrozenList(["flour", "water"])
try:
    hash(unfrozen)
except RuntimeError as exc:
    note(f"Hashing an unfrozen FrozenList raised: <code>{exc}</code>")

# Now invert the mapping: ingredient list -> recipe name.
by_ingredients = {
    freeze_ingredients(ingredients): name
    for name, ingredients in raw_recipes.items()
}

heading("Looking up a recipe by its ingredients")
query = freeze_ingredients(["tomato", "mozzarella", "basil"])
note(f"Query (frozen): <code>{query}</code>")
note(f"Hash of query: <code>{hash(query)}</code>")
note(f"Recipe found: <strong>{by_ingredients.get(query)}</strong>")

# Frozen FrozenLists also work happily inside sets, which lets us
# deduplicate ingredient lists across many recipes.
heading("Deduplicating with a set")
all_ingredient_lists = {
    freeze_ingredients(ings) for ings in raw_recipes.values()
}
all_ingredient_lists.add(freeze_ingredients(["tomato", "mozzarella", "basil"]))
note(
    f"Started with {len(raw_recipes)} recipes, "
    f"set contains {len(all_ingredient_lists)} unique "
    f"ingredient lists (the duplicate Caprese was collapsed)."
)
for ings in sorted(all_ingredient_lists, key=len):
    display(HTML(f"<li><code>{list(ings)}</code></li>"), append=True)

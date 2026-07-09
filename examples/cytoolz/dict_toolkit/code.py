# cytoolz ships a parallel set of dict utilities (`valmap`, `keymap`,
# `merge_with`, etc.) that produce new dicts rather than mutating the
# input. This pairs naturally with the "pure functions" mindset.

heading("1. Mapping and filtering over dicts")

# Sales totals (in USD) for a small bakery, by product.
sales = {
    "sourdough":  1245.50,
    "croissant":   870.25,
    "bagel":       430.00,
    "muffin":      612.75,
    "scone":       198.10,
}

# valmap: transform every value; keys stay the same.
sales_eur = valmap(lambda usd: round(usd * 0.92, 2), sales)
display({"sales in EUR": sales_eur}, append=True)

# valfilter: keep only the items whose value passes a predicate.
top_sellers = valfilter(lambda usd: usd > 500, sales)
display({"top sellers (>$500)": top_sellers}, append=True)

# keymap: rewrite the keys (here, make them display-friendly).
display({"prettified keys": keymap(str.title, sales)}, append=True)

heading("2. Merging dicts, with a combiner for collisions")

monday    = {"sourdough": 12, "croissant":  8, "muffin": 5}
tuesday   = {"sourdough": 10, "bagel":     15, "muffin": 7}
wednesday = {"croissant":  9, "bagel":      6, "scone":  4}

# `merge` does a shallow right-wins merge; `merge_with` lets you say
# how to combine values that share a key. Here we sum daily counts.
weekly_totals = merge_with(sum, monday, tuesday, wednesday)
display({"loaves/pastries sold this week": weekly_totals}, append=True)

heading("3. Nested updates without mutation")
note(
    "<code>assoc</code>, <code>update_in</code> and "
    "<code>get_in</code> let you read and 'update' nested data "
    "while leaving the original untouched."
)

bakery = {
    "name": "The Crumb",
    "address": {"city": "Bristol", "postcode": "BS1 4ST"},
    "menu": {"sourdough": {"price": 5.5, "stock": 12}},
}

# update_in walks a path of keys and applies a function at the leaf.
restocked = update_in(bakery, ["menu", "sourdough", "stock"],
                      lambda n: n + 20)

display({"original stock": get_in(["menu", "sourdough", "stock"], bakery),
         "restocked":      get_in(["menu", "sourdough", "stock"], restocked)},
        append=True)

heading("4. reduceby: group-and-aggregate in a single pass")
note(
    "Like a fused <code>groupby</code> + reduce: walk the iterable "
    "once, keying each item and folding it into its group."
)

transactions = [
    {"category": "food",     "amount": 12.50},
    {"category": "transit",  "amount":  3.20},
    {"category": "food",     "amount":  8.75},
    {"category": "leisure",  "amount": 24.00},
    {"category": "transit",  "amount":  3.20},
    {"category": "food",     "amount": 15.10},
    {"category": "leisure",  "amount":  9.50},
]

spent_by_category = reduceby(
    key="category",
    binop=lambda total, tx: round(total + tx["amount"], 2),
    seq=transactions,
    init=0.0,
)
display({"spent by category": spent_by_category}, append=True)

# ---------------------------------------------------------------------
# Section 2: Generate a patch automatically by diffing two documents.
# ---------------------------------------------------------------------

heading("Diffing two versions of a document")
note(
    "Often you don't write a patch by hand -- you have an old and a new "
    "version of some JSON, and you want the minimal patch that turns one "
    "into the other. <code>jsonpatch.make_patch</code> (also available as "
    "<code>JsonPatch.from_diff</code>) does exactly that."
)

# An order before and after the customer edited their cart.
before = {
    "order_id": "A-1042",
    "customer": {"name": "Grace H.", "city": "Yorktown"},
    "items": [
        {"sku": "BOOK-01", "qty": 1, "price": 12.50},
        {"sku": "MUG-07", "qty": 2, "price": 8.00},
    ],
    "coupon": "SPRING10",
}

after = {
    "order_id": "A-1042",
    "customer": {"name": "Grace Hopper", "city": "Yorktown"},
    "items": [
        {"sku": "BOOK-01", "qty": 2, "price": 12.50},
        {"sku": "MUG-07", "qty": 2, "price": 8.00},
        {"sku": "PEN-03", "qty": 5, "price": 1.25},
    ],
}

show_json("Before", before)
show_json("After", after)

# Compute the patch that transforms `before` into `after`.
diff_patch = jsonpatch.make_patch(before, after)

# JsonPatch is iterable; each element is an operation dict.
note("Generated patch (the smallest set of operations that takes us from before to after):")
show_json("Operations", list(diff_patch))

# Sanity check: applying the patch reproduces `after` exactly.
roundtrip = diff_patch.apply(before)
note(
    "Applying the patch to <code>before</code> reproduces "
    f"<code>after</code> exactly: <strong>{roundtrip == after}</strong>."
)

heading("Patches serialize to JSON for transport")
note(
    "A <code>JsonPatch</code> can be turned into a JSON string with "
    "<code>str()</code> -- handy when you want to send only the changes "
    "over the wire instead of the whole document."
)
display(HTML(f"<pre>{str(diff_patch)}</pre>"), append=True)

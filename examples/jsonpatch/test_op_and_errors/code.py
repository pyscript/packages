# ---------------------------------------------------------------------
# Section 3: Optimistic updates with `test`, plus what happens on failure.
# ---------------------------------------------------------------------

heading("The 'test' operation: optimistic concurrency control")
note(
    "RFC 6902 includes a <code>test</code> op that asserts a value at a "
    "path. If the assertion fails, the whole patch is rejected with a "
    "<code>JsonPatchTestFailed</code> exception. This is the JSON Patch "
    "way of saying 'only apply my changes if the document still looks "
    "like I expect.'"
)

inventory = {
    "sku": "MUG-07",
    "stock": 12,
    "price": 8.00,
}

# Imagine two clients trying to update stock at the same time. Each
# sends a patch that first *tests* the stock level it observed.
patch_alice = jsonpatch.JsonPatch([
    {"op": "test", "path": "/stock", "value": 12},
    {"op": "replace", "path": "/stock", "value": 10},
])

patch_bob = jsonpatch.JsonPatch([
    {"op": "test", "path": "/stock", "value": 12},
    {"op": "replace", "path": "/stock", "value": 9},
])

# Alice applies first -- her test passes.
inventory = patch_alice.apply(inventory)
show_json("After Alice's patch", inventory)

# Now Bob's test fails: stock is no longer 12.
try:
    patch_bob.apply(inventory)
except jsonpatch.JsonPatchTestFailed as exc:
    note(
        f"Bob's patch was rejected: <code>{exc}</code>. "
        "He'd need to re-read the document, re-test, and try again."
    )

heading("Other failure modes")
note(
    "Patches can also fail because a path doesn't exist or an operation "
    "isn't valid for the target. These raise "
    "<code>JsonPatchConflict</code>."
)

bad_patch = jsonpatch.JsonPatch([
    {"op": "remove", "path": "/discount"},  # no such key
])

try:
    bad_patch.apply(inventory)
except jsonpatch.JsonPatchConflict as exc:
    note(f"Removing a missing key raised: <code>{exc}</code>.")

heading("Mutating in place when you really mean it")
note(
    "By default <code>apply</code> returns a new document. Pass "
    "<code>in_place=True</code> if you want to mutate the input directly."
)

bump_price = jsonpatch.JsonPatch([
    {"op": "replace", "path": "/price", "value": 8.50},
])
bump_price.apply(inventory, in_place=True)
show_json("Inventory after in-place price bump", inventory)

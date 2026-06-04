"""
A first look at jsonpatch: applying RFC 6902 operations to a JSON document.

JSON Patch is a small language for describing changes to a JSON document
as a list of operations like `add`, `remove`, `replace`, `move`, `copy`,
and `test`. Each operation targets a location via a JSON Pointer path.

See the spec at https://tools.ietf.org/html/rfc6902 and the package docs
at https://python-json-patch.readthedocs.io/.
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import json
import jsonpatch



def show_json(label, obj):
    """Render a labeled JSON blob as a <pre> block."""
    pretty = json.dumps(obj, indent=2)
    display(HTML(f"<strong>{label}</strong><pre>{pretty}</pre>"), append=True)


# A tiny user profile we'd like to update.
user = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "roles": ["author"],
    "active": False,
}

heading("1. A patch is a list of operations")
note(
    "Each operation has an <code>op</code>, a <code>path</code> (JSON "
    "Pointer), and -- depending on the op -- a <code>value</code> or "
    "<code>from</code>. Here we promote Ada to admin, switch her on, "
    "and tidy up her contact info."
)

operations = [
    {"op": "replace", "path": "/active", "value": True},
    {"op": "add", "path": "/roles/-", "value": "admin"},
    {"op": "add", "path": "/contact", "value": {"email": "ada@example.com"}},
    {"op": "remove", "path": "/email"},
]

patch = jsonpatch.JsonPatch(operations)

show_json("Original document", user)
show_json("Patch", operations)

# `apply` returns a new document by default; the original is untouched.
updated = patch.apply(user)
show_json("Patched document", updated)

note(
    "The path <code>/roles/-</code> means 'append to the array at "
    "<code>/roles</code>'. Note that <code>user</code> itself is "
    "unchanged -- pass <code>in_place=True</code> to mutate it."
)

heading("2. The one-shot helper: apply_patch")
note(
    "If you only need to apply a patch once, skip the object and use "
    "<code>jsonpatch.apply_patch</code>. It accepts either a list of "
    "operations or a JSON string."
)

quick_patch = '[{"op": "replace", "path": "/name", "value": "Ada L."}]'
shorter = jsonpatch.apply_patch(updated, quick_patch)
show_json("After a one-shot patch from a JSON string", shorter)

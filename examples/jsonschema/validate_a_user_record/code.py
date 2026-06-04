"""
A first look at jsonschema: validate user records against a schema.

JSON Schema lets you describe the shape of data declaratively, and
jsonschema is the Python implementation that checks instances against
those schemas. See https://json-schema.org and
https://python-jsonschema.readthedocs.io/ for the full story.
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import jsonschema
from jsonschema import validate, ValidationError


# A schema describing a "user" object: required fields, types, ranges,
# string formats, and an enum for role.
user_schema = {
    "type": "object",
    "required": ["username", "email", "age", "role"],
    "properties": {
        "username": {
            "type": "string",
            "minLength": 3,
            "maxLength": 20,
        },
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 13, "maximum": 130},
        "role": {"enum": ["reader", "author", "admin"]},
    },
    "additionalProperties": False,
}

heading("1. A valid user passes silently")
good_user = {
    "username": "ada_lovelace",
    "email": "ada@example.com",
    "age": 36,
    "role": "author",
}
# validate() raises ValidationError on failure and returns None on success.
validate(instance=good_user, schema=user_schema)
note(f"<code>{good_user}</code> is valid. No exception raised.")

heading("2. An invalid user raises ValidationError")
bad_user = {
    "username": "x",            # too short
    "email": "ada@example.com",
    "age": 36,
    "role": "wizard",           # not in the enum
}

try:
    validate(instance=bad_user, schema=user_schema)
except ValidationError as error:
    note("Caught a <code>ValidationError</code>:")
    display(HTML(f"<pre>{error.message}</pre>"), append=True)
    note(
        f"Failed at path <code>{list(error.absolute_path)}</code> "
        f"on the <code>{error.validator}</code> keyword."
    )

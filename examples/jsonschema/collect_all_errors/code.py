# ---------------------------------------------------------------------
# Iterating over every problem in an instance, instead of stopping at
# the first one. Great for forms and bulk data validation.
# ---------------------------------------------------------------------

import jsonschema
from jsonschema import validate, ValidationError


heading("Lazy validation with iter_errors")
note(
    "<code>validate()</code> stops at the first failure. For richer "
    "feedback, build a Validator and call <code>iter_errors()</code> "
    "to get every problem."
)

# A schema for a small online order.
order_schema = {
    "type": "object",
    "required": ["order_id", "items", "customer"],
    "properties": {
        "order_id": {"type": "string", "pattern": r"^ORD-\d{4}$"},
        "customer": {
            "type": "object",
            "required": ["name", "email"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
            },
        },
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["sku", "quantity", "price"],
                "properties": {
                    "sku": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1},
                    "price": {"type": "number", "minimum": 0},
                },
            },
        },
    },
}

# An order with several intentional problems.
broken_order = {
    "order_id": "12345",          # wrong format
    "customer": {"name": ""},      # empty name, missing email
    "items": [
        {"sku": "A-1", "quantity": 0, "price": 9.99},   # quantity < 1
        {"sku": "B-2", "quantity": 2, "price": -3.00},  # negative price
    ],
}

# Pick a validator class for the JSON Schema draft you're targeting.
Validator = jsonschema.Draft202012Validator
validator = Validator(order_schema)

# is_valid is a quick boolean check.
note(f"<code>is_valid</code> says: <strong>{validator.is_valid(broken_order)}</strong>")

# iter_errors yields every ValidationError found in the instance.
errors = sorted(validator.iter_errors(broken_order), key=lambda e: list(e.absolute_path))

note(f"Found <strong>{len(errors)}</strong> problems:")
rows = ["<table border='1' cellpadding='4' style='border-collapse:collapse'>"]
rows.append("<tr><th>Path</th><th>Keyword</th><th>Message</th></tr>")
for error in errors:
    path = "/".join(str(p) for p in error.absolute_path) or "(root)"
    rows.append(
        f"<tr><td><code>{path}</code></td>"
        f"<td><code>{error.validator}</code></td>"
        f"<td>{error.message}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

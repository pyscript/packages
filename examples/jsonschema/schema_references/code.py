# ---------------------------------------------------------------------
# Splitting a schema into reusable pieces, then wiring them together
# with $ref via a referencing.Registry. This is the modern replacement
# for the deprecated RefResolver.
# ---------------------------------------------------------------------

import jsonschema
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


heading("Composing schemas with a Registry")
note(
    "We define a small <code>address</code> schema once, register it "
    "under a URI, then refer to it from a larger <code>person</code> "
    "schema using <code>$ref</code>."
)

address_schema = {
    "type": "object",
    "required": ["street", "city", "postcode"],
    "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"},
        "postcode": {"type": "string", "pattern": r"^[A-Z0-9 ]{3,10}$"},
    },
}

# Wrap each schema as a Resource bound to a specific JSON Schema draft,
# then build an immutable Registry that maps URIs to these resources.
address_resource = DRAFT202012.create_resource(address_schema)
registry = Registry().with_resource(
    uri="https://example.com/schemas/address",
    resource=address_resource,
)

person_schema = {
    "type": "object",
    "required": ["name", "home_address"],
    "properties": {
        "name": {"type": "string"},
        "home_address": {"$ref": "https://example.com/schemas/address"},
        "work_address": {"$ref": "https://example.com/schemas/address"},
    },
}

# Pass the registry when constructing the Validator so $ref can resolve.
person_validator = Draft202012Validator(person_schema, registry=registry)

heading("A person with two well-formed addresses")
grace = {
    "name": "Grace Hopper",
    "home_address": {
        "street": "1 Cobol Way",
        "city": "Arlington",
        "postcode": "VA 22201",
    },
    "work_address": {
        "street": "2 Compiler Ln",
        "city": "Washington",
        "postcode": "DC 20001",
    },
}
person_validator.validate(grace)
note("Valid! Both addresses pass the referenced schema.")

heading("A person with a malformed work postcode")
alan = {
    "name": "Alan Turing",
    "home_address": {
        "street": "78 High St",
        "city": "Cambridge",
        "postcode": "CB2 1TN",
    },
    "work_address": {
        "street": "Bletchley Park",
        "city": "Milton Keynes",
        "postcode": "lowercase!",   # fails the pattern
    },
}

problems = list(person_validator.iter_errors(alan))
note(f"Found <strong>{len(problems)}</strong> error(s):")
for error in problems:
    path = "/".join(str(p) for p in error.absolute_path) or "(root)"
    display(HTML(f"<pre>at {path}: {error.message}</pre>"), append=True)

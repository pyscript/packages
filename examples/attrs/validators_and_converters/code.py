# ---------------------------------------------------------------------
# Validators check incoming values; converters transform them.
# ---------------------------------------------------------------------

heading("Catching bad data at construction time")
note(
    "We model a coffee order. The <code>size</code> must be one of a "
    "few known values, the <code>shots</code> must be a positive int, "
    "and <code>name</code> is automatically stripped and title-cased."
)


def clean_name(value: str) -> str:
    """Converter: tidy up a customer's name before storing it."""
    return value.strip().title()


@define
class CoffeeOrder:
    name: str = field(converter=clean_name)
    size: str = field(validator=attrs.validators.in_(["small", "medium", "large"]))
    shots: int = field(
        default=1,
        validator=[attrs.validators.instance_of(int), attrs.validators.gt(0)],
    )
    notes: str = field(default="")


# Happy path: converter cleans the name, validators are satisfied.
order = CoffeeOrder(name="  ada lovelace ", size="large", shots=2)
note(f"Cleaned name: <code>{order.name!r}</code>")
display(order, append=True)

# Now demonstrate what happens when validation fails. We catch each
# error so the example keeps running and shows all the failure modes.
heading("Validation errors are raised early and clearly")

bad_inputs = [
    {"name": "Bob", "size": "huge", "shots": 1},        # bad size
    {"name": "Carol", "size": "small", "shots": 0},     # not > 0
    {"name": "Dan", "size": "medium", "shots": "two"},  # wrong type
]

for kwargs in bad_inputs:
    try:
        CoffeeOrder(**kwargs)
    except (ValueError, TypeError) as err:
        note(f"<code>{kwargs}</code> &rarr; <strong>{type(err).__name__}</strong>: {err}")

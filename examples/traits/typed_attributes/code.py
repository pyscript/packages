"""
A first look at Traits: declare typed, validated attributes on a class
by inheriting from HasTraits and assigning trait types as class
attributes.

Docs: https://docs.enthought.com/traits/
"""
from IPython.core.display import display, HTML


# Define a class whose attributes are *traits*: each one declares a
# type, a default, and (optionally) constraints. Validation happens
# automatically on every assignment.
class Espresso(HasTraits):
    name = Str("House blend")
    shots = Range(low=1, high=4, value=2)         # bounded integer
    ounces = Float(2.0)                            # any float
    temperature_c = Int(92)                        # any integer
    milk = Enum("none", "steamed", "foamed")       # one of a fixed set
    decaf = Bool(False)
    notes = List(Str)                              # list of strings


heading("1. Defaults appear without an __init__")
drink = Espresso()
note(
    "We never wrote an <code>__init__</code>, but the instance already "
    "has sensible defaults pulled from each trait declaration."
)
display(HTML(
    f"<pre>name={drink.name!r}\nshots={drink.shots}\n"
    f"milk={drink.milk!r}\ndecaf={drink.decaf}</pre>"
), append=True)


heading("2. Keyword-style construction")
latte = Espresso(name="Morning latte", shots=2, milk="steamed", ounces=8.0)
note("HasTraits accepts trait values as keyword arguments.")
display(HTML(f"<pre>{latte.trait_get('name', 'shots', 'milk', 'ounces')}</pre>"),
        append=True)


heading("3. Validation rejects bad values")
note(
    "Assigning the wrong type or an out-of-range value raises "
    "<code>TraitError</code> immediately, at the point of the bad "
    "assignment, instead of failing mysteriously later."
)
attempts = [
    ("latte.shots = 99", lambda: setattr(latte, "shots", 99)),       # out of range
    ("latte.milk = 'whipped'", lambda: setattr(latte, "milk", "whipped")),  # not in enum
    ("latte.temperature_c = '92'", lambda: setattr(latte, "temperature_c", "92")),  # wrong type
]
results = []
for label, action in attempts:
    try:
        action()
        results.append(f"{label}  -> accepted (unexpected!)")
    except Exception as exc:
        results.append(f"{label}  -> {type(exc).__name__}: {exc}")
display(HTML("<pre>" + "\n\n".join(results) + "</pre>"), append=True)

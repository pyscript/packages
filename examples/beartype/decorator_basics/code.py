"""
A first look at beartype.

Beartype turns ordinary PEP 484 type hints into fast runtime checks.
Decorate any annotated function with @beartype and it will raise a
clear, descriptive exception the moment a caller passes the wrong
type or your function returns the wrong type.

Docs: https://beartype.readthedocs.io
"""
from IPython.core.display import display, HTML


from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation


# A small inventory function. Note the standard, ordinary type hints:
# beartype reads these directly. No special syntax required.
@beartype
def restock(item: str, quantity: int, on_sale: bool = False) -> dict:
    """Build a tiny restock record for one product."""
    price = 9.99 * (0.8 if on_sale else 1.0)
    return {"item": item, "quantity": quantity, "unit_price": round(price, 2)}


heading("1. A well-behaved call")
note("With matching types, @beartype is invisible — the function just runs.")
record = restock("notebook", 12, on_sale=True)
display(record, append=True)


heading("2. A call with the wrong parameter type")
note(
    "We pass a string where an int is expected. Beartype intercepts the call "
    "before the function body runs and raises a precise exception."
)
try:
    restock("pencil", "twelve")
except BeartypeCallHintParamViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)


heading("3. A call where the function returns the wrong type")
note(
    "Beartype also checks return values. Here we deliberately wrap a "
    "function whose body lies about its return type."
)

@beartype
def average(values: list[float]) -> float:
    # Oops — returning a list instead of a float.
    return values

try:
    average([1.0, 2.0, 3.0])
except BeartypeCallHintReturnViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)

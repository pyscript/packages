# ---------------------------------------------------------------------
# under_cached_property: store cached values in `self._cache`
# ---------------------------------------------------------------------

heading("When you want a separate cache dict: under_cached_property")
note(
    "<code>under_cached_property</code> behaves like "
    "<code>cached_property</code>, but it stores results in "
    "<code>self._cache</code> instead of <code>self.__dict__</code>. "
    "It also disallows <code>__set__</code>, so the property is "
    "read-only. This is handy on classes that use "
    "<code>__slots__</code> or that want a single, easily "
    "inspectable place to clear cached state."
)


class Order:
    """A small order whose totals are cached in `self._cache`."""

    __slots__ = ("items", "tax_rate", "_cache")

    def __init__(self, items, tax_rate):
        self.items = items  # list of (name, unit_price, quantity)
        self.tax_rate = tax_rate
        # under_cached_property requires this attribute to exist.
        self._cache = {}

    @under_cached_property
    def subtotal(self):
        return sum(price * qty for _, price, qty in self.items)

    @under_cached_property
    def total(self):
        return round(self.subtotal * (1 + self.tax_rate), 2)


order = Order(
    items=[
        ("Notebook", 4.50, 3),
        ("Pen", 1.20, 10),
        ("Stapler", 8.99, 1),
    ],
    tax_rate=0.08,
)

note("Asking for the total computes and caches both properties:")
display(f"total = {order.total}")
display(f"_cache contents = {order._cache}")

note(
    "Because the cache is just a dict on the instance, you can clear "
    "specific entries to invalidate them, e.g. after changing the "
    "tax rate:"
)
order.tax_rate = 0.10
order._cache.pop("total", None)
display(f"new total = {order.total}")
display(f"_cache contents = {order._cache}")

note(
    "Trying to assign to an <code>under_cached_property</code> raises "
    "<code>AttributeError</code>, which protects the cached value "
    "from accidental overwrites:"
)
try:
    order.subtotal = 999.99
except AttributeError as exc:
    display(f"AttributeError: {exc}")

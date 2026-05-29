# Dynamic defaults computed at first access, plus callbacks that fire
# whenever a trait changes.

heading("Dynamic defaults with @default")
note(
    "Use <code>@default('trait_name')</code> to compute a default value "
    "the first time the trait is accessed, instead of at class-definition "
    "time."
)


class Order(HasTraits):
    """A coffee order with a default size that depends on the drink."""
    drink = Unicode("espresso")
    size_ml = Int()

    @default("size_ml")
    def _default_size(self):
        # Espresso is small; everything else gets a generous pour.
        return 30 if self.drink == "espresso" else 240


for drink in ["espresso", "latte", "americano"]:
    order = Order(drink=drink)
    display(HTML(
        f"<pre>{order.drink:<10} default size = {order.size_ml} ml</pre>"
    ), append=True)


heading("Observing trait changes with @observe")
note(
    "Decorate a method with <code>@observe('trait_name')</code> to be "
    "called whenever the trait's value changes. The callback receives a "
    "dict with <code>name</code>, <code>old</code>, <code>new</code>, "
    "<code>owner</code>, and <code>type</code>."
)


class Thermostat(HasTraits):
    """A thermostat that logs every target-temperature change."""
    target_celsius = Float(20.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []

    @observe("target_celsius")
    def _on_target_changed(self, change):
        self.history.append(
            f"{change['old']:.1f} -> {change['new']:.1f}"
        )


thermostat = Thermostat()
for new_target in [21.0, 22.5, 19.0, 23.5]:
    thermostat.target_celsius = new_target

note("Recorded transitions:")
display(HTML(
    "<pre>" + "\n".join(thermostat.history) + "</pre>"
), append=True)

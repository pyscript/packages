# Custom validators reject or transform incoming values, and `link`
# keeps two traits on different objects in sync.

heading("Custom validation with @validate")
note(
    "A validator receives a <code>proposal</code> dict and must return "
    "the value to store (or raise <code>TraitError</code> to reject it)."
)


class BankAccount(HasTraits):
    """An account that refuses overdrafts and rounds to whole cents."""
    holder = Unicode("anonymous")
    balance_cents = Int(0)

    @validate("balance_cents")
    def _check_balance(self, proposal):
        new_value = proposal["value"]
        if new_value < 0:
            raise TraitError(
                f"balance_cents must be >= 0, got {new_value}"
            )
        return new_value


account = BankAccount(holder="Ada", balance_cents=12_345)
display(HTML(
    f"<pre>{account.holder}: {account.balance_cents / 100:.2f}</pre>"
), append=True)

try:
    account.balance_cents = -500
except TraitError as error:
    display(HTML(f"<pre>Rejected: {error}</pre>"), append=True)


heading("Linking traits across objects")
note(
    "<code>link((source, 'trait'), (target, 'trait'))</code> mirrors "
    "changes from the source onto the target. This is how Jupyter "
    "widgets stay synchronised."
)


class Slider(HasTraits):
    value = Float(0.0)


class Display(HasTraits):
    reading = Float(0.0)


slider = Slider()
readout = Display()
mirror = link((slider, "value"), (readout, "reading"))

slider.value = 3.14
display(HTML(
    f"<pre>after slider.value = 3.14\n"
    f"  slider.value   = {slider.value}\n"
    f"  readout.reading = {readout.reading}</pre>"
), append=True)

slider.value = 42.0
display(HTML(
    f"<pre>after slider.value = 42.0\n"
    f"  slider.value   = {slider.value}\n"
    f"  readout.reading = {readout.reading}</pre>"
), append=True)

# Unlink to stop mirroring; the readout now stays put.
mirror.unlink()
slider.value = 99.0
note("After <code>mirror.unlink()</code>, the readout is no longer updated:")
display(HTML(
    f"<pre>slider.value    = {slider.value}\n"
    f"readout.reading = {readout.reading}</pre>"
), append=True)

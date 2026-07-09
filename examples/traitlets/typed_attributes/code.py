"""
A first look at traitlets.

Traitlets lets you give Python classes attributes that enforce types,
validate values, and notify you when they change. It powers IPython
and Jupyter's configuration and widget systems.

Docs: https://traitlets.readthedocs.io/
"""
from IPython.core.display import display, HTML
from traitlets import HasTraits, Unicode, Int, Float, TraitError


# Subclass HasTraits and declare typed attributes as class-level traits.
# Each trait can have a default and a help string.
class Thermostat(HasTraits):
    """A small device with strongly typed settings."""
    name = Unicode("kitchen")
    target_celsius = Float(20.0)
    fan_speed = Int(2, help="Fan speed from 0 (off) to 5 (max).")


heading("1. Declaring traits")
note(
    "Traits behave like regular attributes, but the type is enforced "
    "every time you assign to them."
)

thermostat = Thermostat(name="living-room", target_celsius=21.5)
display(HTML(
    f"<pre>name           = {thermostat.name!r}\n"
    f"target_celsius = {thermostat.target_celsius}\n"
    f"fan_speed      = {thermostat.fan_speed}</pre>"
), append=True)

heading("2. Type enforcement", level=3)
note(
    "Assigning a value of the wrong type raises a TraitError. Try "
    "setting <code>fan_speed</code> to a string:"
)

try:
    thermostat.fan_speed = "high"
except TraitError as error:
    display(HTML(f"<pre>TraitError: {error}</pre>"), append=True)

heading("3. Coercion of compatible types", level=3)
note(
    "Floats accept integer assignments and coerce them, so this "
    "succeeds and stores 19.0:"
)
thermostat.target_celsius = 19
display(HTML(
    f"<pre>target_celsius = {thermostat.target_celsius!r}</pre>"
), append=True)

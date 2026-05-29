# ---------------------------------------------------------------------
# Section 2: Pickling a class defined here, plus instances of it.
# ---------------------------------------------------------------------

heading("Shipping a dynamically-defined class")
note(
    "Imagine you're prototyping a small data model in a notebook and "
    "want to send a few instances to a worker process for scoring. "
    "cloudpickle bundles both the class definition and the instance "
    "state into the payload."
)

class SensorReading:
    """A single reading from a temperature sensor."""

    def __init__(self, sensor_id, celsius):
        self.sensor_id = sensor_id
        self.celsius = celsius

    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    def __repr__(self):
        return (
            f"SensorReading(sensor_id={self.sensor_id!r}, "
            f"celsius={self.celsius})"
        )


readings = [
    SensorReading("kitchen", 21.5),
    SensorReading("garden", 8.2),
    SensorReading("attic", 31.0),
]

# Pickle the whole list -- class and instances together.
payload = cloudpickle.dumps(readings)
note(f"Serialized {len(readings)} readings into {len(payload)} bytes.")

# Simulate "the worker" by deleting the class locally before unpickling.
# cloudpickle stored the class by value, so this still works.
del SensorReading

restored = pickle.loads(payload)

note("After deleting the class locally and unpickling:")
for r in restored:
    display(HTML(
        f"<code>{r!r}</code> &rarr; "
        f"<strong>{r.fahrenheit():.1f} &deg;F</strong>"
    ), append=True)

heading("Pickling the class itself")
note(
    "You can also send the class on its own, then construct fresh "
    "instances on the receiving side."
)

ClassPayload = cloudpickle.dumps(type(restored[0]))
RemoteSensorReading = pickle.loads(ClassPayload)

fresh = RemoteSensorReading("basement", 14.0)
note(
    f"Constructed a new instance from the unpickled class: "
    f"<code>{fresh!r}</code>, which reports "
    f"<strong>{fresh.fahrenheit():.1f} &deg;F</strong>."
)

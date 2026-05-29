"""
A first taste of JMESPath: a tiny query language for JSON-shaped data.

JMESPath lets you declaratively pull values out of nested dicts and
lists, the same way you might use a CSS selector or an XPath query.
See https://jmespath.org/tutorial.html for the language reference.
"""
from IPython.core.display import display, HTML

# A made-up response from a "fleet" API: a handful of delivery vans,
# each with some nested details.
fleet = {
    "company": "Fern & Foxglove Deliveries",
    "vans": [
        {"id": "V-01", "driver": "Ada",   "mileage": 48210, "active": True},
        {"id": "V-02", "driver": "Bram",  "mileage": 12044, "active": False},
        {"id": "V-03", "driver": "Cleo",  "mileage": 91577, "active": True},
        {"id": "V-04", "driver": "Dario", "mileage": 30100, "active": True},
    ],
}

heading("1. Reaching into nested data")
note("Use dot notation to walk down through keys.")

company = jmespath.search("company", fleet)
note(f"Company name: <strong>{company}</strong>")

# Index into the list of vans, then read a field on that item.
first_driver = jmespath.search("vans[0].driver", fleet)
last_driver = jmespath.search("vans[-1].driver", fleet)
note(
    f"First van's driver: <strong>{first_driver}</strong>. "
    f"Last van's driver: <strong>{last_driver}</strong>."
)

heading("2. Projecting across a list")
note(
    "The <code>[*]</code> wildcard projects an expression over every "
    "element of a list and collects the results."
)

all_drivers = jmespath.search("vans[*].driver", fleet)
display(HTML(f"<pre>vans[*].driver -> {all_drivers}</pre>"), append=True)

# Combine fields into a new shape with a multi-select hash.
summary = jmespath.search("vans[*].{who: driver, miles: mileage}", fleet)
note("Reshape each van into a smaller record:")
display(summary, append=True)

"""
A first taste of PyYAML: parsing a YAML configuration string into
Python data, and serializing Python data back into YAML.

PyYAML is the standard YAML parser and emitter for Python. It's the
go-to choice for reading config files, fixtures, CI workflows, and
similar human-friendly data.

Docs: https://pyyaml.org/wiki/PyYAMLDocumentation
"""
from IPython.core.display import display, HTML

import yaml


# A config file as you might find one in a project's repo.
config_text = """
service: weather-api
version: 2.4
debug: true
allowed_hosts:
  - localhost
  - api.example.com
limits:
  requests_per_minute: 60
  burst: 10
"""

heading("1. Parsing YAML with safe_load")
note(
    "<code>yaml.safe_load</code> turns a YAML string (or open file) "
    "into ordinary Python objects: dicts, lists, strings, numbers, "
    "and booleans. Always prefer <code>safe_load</code> over "
    "<code>load</code> for untrusted input."
)

config = yaml.safe_load(config_text)

note(f"Type of the parsed object: <code>{type(config).__name__}</code>")
note(f"Service name: <strong>{config['service']}</strong>")
note(f"Allowed hosts: <code>{config['allowed_hosts']}</code>")
note(f"Burst limit: <code>{config['limits']['burst']}</code>")

heading("2. Dumping Python data back to YAML")
note(
    "<code>yaml.safe_dump</code> takes a Python object and produces "
    "a YAML string. Pass <code>default_flow_style=False</code> for "
    "the readable block style; <code>sort_keys=False</code> "
    "preserves the dict's insertion order."
)

# Build a small Python structure and round-trip it through YAML.
release = {
    "name": "weather-api",
    "version": "2.5.0",
    "released": "2026-04-01",
    "highlights": [
        "Faster forecast lookups",
        "New /alerts endpoint",
        "Improved error messages",
    ],
}

yaml_text = yaml.safe_dump(
    release,
    default_flow_style=False,
    sort_keys=False,
)

display(HTML(f"<pre>{yaml_text}</pre>"), append=True)

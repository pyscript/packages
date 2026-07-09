"""
A first look at strictyaml: parse YAML with a typed schema.

StrictYAML is a type-safe YAML parser. Without a schema, every value
comes back as a string. With a schema, values are cast to the right
Python types, and clear errors are raised if the document does not
conform.

See https://hitchdev.com/strictyaml for more.
"""
from IPython.core.display import display, HTML

import strictyaml
from strictyaml import (
    load, as_document, Map, MapPattern, Seq, FixedSeq, Optional,
    Str, Int, Float, Bool, Decimal, Datetime, Enum, Regex,
    CommaSeparated, EmptyNone, YAMLError,
)


# A small bit of YAML describing a fictional character.
character_yaml = """
# All about the character
name: Ford Prefect
age: 42
possessions:
  - Towel
  - Babel fish
  - Electronic Thumb
"""

heading("1. Parsing without a schema")
note(
    "Without a schema, every leaf value is a string. Notice that "
    "<code>age</code> below is the string '42', not the integer 42."
)
untyped = load(character_yaml)
display(untyped.data, append=True)

heading("2. Parsing with a schema")
note(
    "Define a schema with <code>Map</code>, <code>Seq</code>, "
    "<code>Str</code>, and <code>Int</code>. Now <code>age</code> "
    "is parsed as a real integer."
)

character_schema = Map({
    "name": Str(),
    "age": Int(),
    "possessions": Seq(Str()),
})

character = load(character_yaml, character_schema)
display(character.data, append=True)
note(f"Type of age: <code>{type(character['age'].data).__name__}</code>")

heading("3. Catching schema violations")
note(
    "If the YAML doesn't match the schema, strictyaml raises a "
    "<code>YAMLError</code> with a friendly message that points "
    "at the offending line."
)

bad_yaml = """
name: Arthur Dent
age: forty-two
possessions:
  - Dressing gown
"""

try:
    load(bad_yaml, character_schema)
except YAMLError as error:
    display(HTML(f"<pre>{error}</pre>"), append=True)

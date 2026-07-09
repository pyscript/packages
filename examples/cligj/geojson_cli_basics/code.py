"""
Introducing cligj: reusable Click options and arguments for command line
tools that consume and produce GeoJSON.

cligj doesn't define a CLI of its own; instead it gives you battle-tested
decorators (like `features_in_arg`, `sequence_opt`, `use_rs_opt`) that
you stack onto your own Click commands so they accept GeoJSON in all the
shapes geospatial users expect: a file, stdin, a feature collection, or
a sequence of features.

See the package docs at https://github.com/mapbox/cligj for the full set
of arguments and options.
"""
from IPython.core.display import display, HTML

import json
import click
import cligj
from click.testing import CliRunner

# A small synthetic FeatureCollection used as input throughout the
# examples. Three notable points in Europe with a "name" property.
SAMPLE_FEATURES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Eiffel Tower"},
            "geometry": {
                "type": "Point",
                "coordinates": [2.2945, 48.8584],
            },
        },
        {
            "type": "Feature",
            "properties": {"name": "Colosseum"},
            "geometry": {
                "type": "Point",
                "coordinates": [12.4922, 41.8902],
            },
        },
        {
            "type": "Feature",
            "properties": {"name": "Brandenburg Gate"},
            "geometry": {
                "type": "Point",
                "coordinates": [13.3777, 52.5163],
            },
        },
    ],
}


heading("A first cligj-powered command")
note(
    "We define a Click command, <code>list_names</code>, that uses "
    "<code>cligj.features_in_arg</code> to accept GeoJSON input. The "
    "decorator turns a positional argument into an iterable of "
    "Feature-like dicts, regardless of whether the input is a "
    "FeatureCollection or a sequence of features."
)


@click.command()
@cligj.features_in_arg
def list_names(features):
    """Print the 'name' property of every input feature."""
    for feature in features:
        name = feature["properties"].get("name", "<unnamed>")
        click.echo(name)


# Click commands are normally invoked from a shell. In a notebook or
# browser we use Click's CliRunner to invoke them in-process and
# capture their stdout. We pass our sample FeatureCollection on stdin.
runner = CliRunner()
sample_text = json.dumps(SAMPLE_FEATURES)

result = runner.invoke(list_names, args=["-"], input=sample_text)

note("Command output:")
display(HTML(f"<pre>{result.output}</pre>"), append=True)

note(
    "Notice we never wrote any GeoJSON-parsing code: cligj normalized "
    "the input into an iterator of features for us."
)

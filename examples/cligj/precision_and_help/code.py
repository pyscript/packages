# Coordinate precision and auto-generated help
#
# cligj also supplies smaller utility options. `precision_opt` is a
# common one: it exposes a `--precision N` flag for rounding coordinate
# values, which is useful for shrinking output or normalizing data
# before diffing.

import json
import click
import cligj
from click.testing import CliRunner

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


heading("A rounding filter built from cligj options")
note(
    "We combine <code>features_in_arg</code> with "
    "<code>precision_opt</code> and <code>indent_opt</code> to build "
    "a tiny but realistic GeoJSON formatter."
)


def round_coords(coords, precision):
    """Recursively round numeric coordinates to `precision` decimals."""
    if isinstance(coords, (int, float)):
        return round(coords, precision)
    return [round_coords(c, precision) for c in coords]


@click.command()
@cligj.features_in_arg
@cligj.precision_opt
@cligj.indent_opt
def round_features(features, precision, indent):
    """Round each feature's coordinates and pretty-print the result."""
    rounded = []
    for feature in features:
        new_feature = dict(feature)
        if precision is not None and "geometry" in new_feature:
            geom = dict(new_feature["geometry"])
            geom["coordinates"] = round_coords(
                geom["coordinates"], precision,
            )
            new_feature["geometry"] = geom
        rounded.append(new_feature)

    click.echo(json.dumps(
        {"type": "FeatureCollection", "features": rounded},
        indent=indent,
    ))


runner = CliRunner()
sample_text = json.dumps(SAMPLE_FEATURES)

note("Round to 1 decimal place, indent with 2 spaces:")
result = runner.invoke(
    round_features,
    args=["-", "--precision", "1", "--indent", "2"],
    input=sample_text,
)
display(HTML(f"<pre>{result.output}</pre>"), append=True)

heading("Auto-generated --help", level=3)
note(
    "Because cligj's decorators are real Click options, your command "
    "gets a polished <code>--help</code> screen for free."
)
help_result = runner.invoke(round_features, args=["--help"])
display(HTML(f"<pre>{help_result.output}</pre>"), append=True)

note(
    "That's the cligj philosophy: assemble small, well-named, "
    "well-documented Click decorators into CLIs that feel familiar to "
    "anyone who has used <code>fio</code>, <code>rio</code>, or other "
    "tools in the Mapbox/Python geospatial ecosystem."
)

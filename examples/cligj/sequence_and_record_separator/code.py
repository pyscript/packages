# Feature collections vs. feature sequences
#
# Geospatial pipelines often prefer streaming one feature per line over
# loading a whole FeatureCollection at once. cligj's `sequence_opt` and
# `use_rs_opt` make this a one-line opt-in for your CLI users.

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


heading("A pass-through command with --sequence and --rs")
note(
    "This is the canonical example from cligj's README, distilled. "
    "The same command can emit a FeatureCollection (the default), a "
    "newline-delimited sequence, or an "
    "<a href='https://tools.ietf.org/html/rfc8142'>RFC 8142</a> "
    "GeoJSON Text Sequence prefixed with the 0x1E record separator."
)


@click.command()
@cligj.features_in_arg
@cligj.sequence_opt
@cligj.use_rs_opt
def pass_features(features, sequence, use_rs):
    """Echo features either as a collection or a sequence."""
    if sequence:
        for feature in features:
            if use_rs:
                click.echo("\x1e", nl=False)
            click.echo(json.dumps(feature))
    else:
        click.echo(json.dumps({
            "type": "FeatureCollection",
            "features": list(features),
        }))


runner = CliRunner()
sample_text = json.dumps(SAMPLE_FEATURES)


def run(label, extra_args):
    result = runner.invoke(
        pass_features, args=["-", *extra_args], input=sample_text,
    )
    # Visualize the 0x1E record separator as a printable marker so
    # readers can see where it sits in the output.
    visible = result.output.replace("\x1e", "[RS]")
    note(f"<strong>{label}</strong> &mdash; "
         f"<code>pass_features {' '.join(extra_args) or '(no flags)'}</code>")
    display(HTML(f"<pre>{visible}</pre>"), append=True)


run("Default: a single FeatureCollection", [])
run("Sequence: one feature per line", ["--sequence"])
run("RFC 8142 text sequence with record separators",
    ["--sequence", "--rs"])

note(
    "Same command, three idiomatic output modes &mdash; and your "
    "implementation only had to check two booleans."
)

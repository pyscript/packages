"""
A first look at Click: turn a regular Python function into a
command line interface with a couple of decorators.

Click docs: https://click.palletsprojects.com/
"""
from IPython.core.display import display, HTML

# ---------------------------------------------------------------------
# Section 1: Decorate a function to make it a command.
# ---------------------------------------------------------------------

heading("1. From function to CLI")
note(
    "We define a tiny <code>greet</code> command with one option "
    "and one argument, then invoke it the way a shell would."
)


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.argument("name")
def greet(count, name):
    """Greet NAME a given number of times."""
    for _ in range(count):
        click.echo(f"Hello, {name}!")


# Invoke the command with command-line-style arguments. No real
# shell needed: CliRunner runs it in-process and captures stdout.
note("Running: <code>greet --count 3 Ada</code>")
result = runner.invoke(greet, ["--count", "3", "Ada"])
show_output(result)

# ---------------------------------------------------------------------
# Section 2: Click writes the --help page for you.
# ---------------------------------------------------------------------

heading("2. Free help text")
note(
    "Click derives the help page from the docstring, options, and "
    "arguments. Try <code>--help</code> on any Click command:"
)
result = runner.invoke(greet, ["--help"])
show_output(result)

# ---------------------------------------------------------------------
# Section 3: Validation comes for free.
# ---------------------------------------------------------------------

heading("3. Built-in validation")
note(
    "Pass a non-integer to <code>--count</code> and Click reports a "
    "friendly error and a non-zero exit code, without us writing any "
    "validation code ourselves."
)
result = runner.invoke(greet, ["--count", "not-a-number", "Ada"])
show_output(result)

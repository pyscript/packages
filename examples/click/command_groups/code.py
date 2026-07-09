# ---------------------------------------------------------------------
# Section 1: A command group with shared state via the context.
# ---------------------------------------------------------------------click
from click.testing import CliRunner

heading("1. A tiny todo CLI with subcommands")
note(
    "Real CLIs (think <code>git</code> or <code>docker</code>) "
    "have many subcommands. Click groups make this easy: decorate "
    "a parent function with <code>@click.group()</code> and attach "
    "child commands with <code>@parent.command()</code>."
)

# A shared in-memory store that pretends to be our database.
todo_store = {"items": ["Write docs", "Review PR #42"]}


@click.group()
@click.option("--verbose", is_flag=True, help="Show extra output.")
@click.pass_context
def todo(ctx, verbose):
    """Manage a small todo list."""
    # ctx.obj is the canonical place to stash state for subcommands.
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["store"] = todo_store


@todo.command("list")
@click.pass_context
def list_items(ctx):
    """Show all todo items."""
    items = ctx.obj["store"]["items"]
    if ctx.obj["verbose"]:
        click.echo(f"({len(items)} items)")
    for i, item in enumerate(items, start=1):
        click.echo(f"{i}. {item}")


@todo.command("add")
@click.argument("text")
@click.pass_context
def add_item(ctx, text):
    """Add a new item to the list."""
    ctx.obj["store"]["items"].append(text)
    click.secho(f"Added: {text}", fg="green")


@todo.command("done")
@click.argument("index", type=click.IntRange(min=1))
@click.pass_context
def done_item(ctx, index):
    """Mark item INDEX as done by removing it."""
    items = ctx.obj["store"]["items"]
    if index > len(items):
        raise click.BadParameter(f"No item at position {index}.")
    removed = items.pop(index - 1)
    click.secho(f"Done: {removed}", fg="cyan")


# ---------------------------------------------------------------------
# Section 2: Drive the group like a user would.
# ---------------------------------------------------------------------

heading("2. Driving the group")

note("List the starting items:")
show_output(runner.invoke(todo, ["list"]))

note("Add a new item:")
show_output(runner.invoke(todo, ["add", "Buy more coffee"]))

note("List again, this time with <code>--verbose</code>:")
show_output(runner.invoke(todo, ["--verbose", "list"]))

note("Mark item 1 as done:")
show_output(runner.invoke(todo, ["done", "1"]))

note(
    "<code>IntRange</code> rejects bad input. Try index 0 to see "
    "Click's automatic validation:"
)
show_output(runner.invoke(todo, ["done", "0"]))

# ---------------------------------------------------------------------
# Section 3: Auto-generated help for the whole group.
# ---------------------------------------------------------------------

heading("3. Help for the whole group")
note(
    "Groups produce a top-level help page that lists subcommands, "
    "and each subcommand has its own <code>--help</code>."
)
show_output(runner.invoke(todo, ["--help"]))
show_output(runner.invoke(todo, ["add", "--help"]))

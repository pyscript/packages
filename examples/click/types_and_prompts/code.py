# ---------------------------------------------------------------------
# Section 1: Parameter types and choices.
# ---------------------------------------------------------------------

heading("1. Typed options and click.Choice")
note(
    "Click converts and validates option values for you. Here we "
    "build a tiny <code>order</code> command for a coffee shop with "
    "an integer count, a float price, and a constrained drink name."
)


@click.command()
@click.option("--drink", type=click.Choice(
    ["espresso", "latte", "mocha"], case_sensitive=False,
), required=True, help="Which drink to order.")
@click.option("--count", type=int, default=1, show_default=True,
              help="How many to order.")
@click.option("--price", type=float, default=3.50, show_default=True,
              help="Unit price in dollars.")
def order(drink, count, price):
    """Place a coffee order and print the total."""
    total = count * price
    click.echo(f"{count} x {drink.lower()} @ ${price:.2f} = ${total:.2f}")


note("A valid order:")
result = runner.invoke(order, ["--drink", "Latte", "--count", "2"])
show_output(result)

note("An invalid choice is rejected with a helpful message:")
result = runner.invoke(order, ["--drink", "tea"])
show_output(result)

# ---------------------------------------------------------------------
# Section 2: Prompts and confirmations.
# ---------------------------------------------------------------------

heading("2. Prompting for missing values")
note(
    "If an option is marked <code>prompt=True</code>, Click asks "
    "for it interactively when it's not supplied. CliRunner can "
    "feed simulated input via the <code>input=</code> parameter."
)


@click.command()
@click.option("--name", prompt="Your name",
              help="Who is signing up?")
@click.option("--newsletter", is_flag=True,
              prompt="Subscribe to the newsletter?",
              help="Opt in to email updates.")
def signup(name, newsletter):
    """Register a user."""
    sub = "subscribed" if newsletter else "not subscribed"
    click.echo(f"Welcome, {name}! You are {sub}.")


# Simulate a user typing "Grace" then "y" at the two prompts.
note("Simulating input: <code>Grace</code>, then <code>y</code>")
result = runner.invoke(signup, [], input="Grace\ny\n")
show_output(result)

# Supplying values up front skips the prompts entirely.
note("Passing values on the command line skips both prompts:")
result = runner.invoke(signup, ["--name", "Hopper", "--newsletter"])
show_output(result)

# ---------------------------------------------------------------------
# Sometimes a type alone isn't enough. You want "a non-empty list of
# strings" or "a positive integer". Beartype validators let you attach
# arbitrary boolean predicates to any type using typing.Annotated.
# ---------------------------------------------------------------------

heading("1. Defining reusable validated types")
note(
    "An Annotated[T, Is[lambda x: ...]] hint means 'a T that also satisfies "
    "this lambda'. You can stack multiple Is[...] clauses with & and |."
)

# Reusable building blocks.
PositiveInt = Annotated[int, Is[lambda n: n > 0]]
NonEmptyStr = Annotated[str, Is[lambda s: len(s.strip()) > 0]]
Percentage = Annotated[float, Is[lambda x: 0.0 <= x <= 100.0]]


@beartype
def record_score(student: NonEmptyStr, attempts: PositiveInt, score: Percentage) -> str:
    """Format a single grading record."""
    return f"{student}: {score:.1f}% over {attempts} attempt(s)"


heading("2. Valid input passes through")
display(record_score("Hypatia", 3, 92.5), append=True)
display(record_score("Turing", 1, 100.0), append=True)


heading("3. Each validator catches its own kind of mistake")
note("Empty student name — fails the NonEmptyStr predicate:")
try:
    record_score("   ", 2, 80.0)
except BeartypeCallHintParamViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)

note("Zero attempts — fails the PositiveInt predicate:")
try:
    record_score("Lovelace", 0, 75.0)
except BeartypeCallHintParamViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)

note("Score above 100 — fails the Percentage range predicate:")
try:
    record_score("Noether", 2, 120.0)
except BeartypeCallHintParamViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)


heading("4. Composing validators with &")
note(
    "Validators compose with & (and) and | (or). Here we require a string "
    "that is both non-empty AND all lowercase — perfect for slugs."
)

Slug = Annotated[
    str,
    Is[lambda s: len(s) > 0] & Is[lambda s: s == s.lower()] & Is[lambda s: " " not in s],
]


@beartype
def make_url(base: NonEmptyStr, slug: Slug) -> str:
    return f"{base.rstrip('/')}/{slug}"


display(make_url("https://example.com", "hello-world"), append=True)

note("And a slug with uppercase letters is rejected:")
try:
    make_url("https://example.com", "Hello World")
except BeartypeCallHintParamViolation as exc:
    display(HTML(f"<pre style='white-space:pre-wrap'>{exc}</pre>"), append=True)

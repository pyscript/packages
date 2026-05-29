# Pipelines: thread a value through a sequence of small, pure functions.
# `pipe(value, f, g, h)` is equivalent to `h(g(f(value)))`, but reads
# top-to-bottom in the order things actually happen.

heading("1. pipe: a value flowing through transformations")

# Daily temperature readings in Celsius from a weather station.
readings_c = [-3.0, 1.5, 4.2, 7.8, 12.4, 18.1, 22.6, 19.3, 11.0, 5.5]


def to_fahrenheit(c):
    return c * 9 / 5 + 32


def is_above_freezing(f):
    return f > 32


# `cytoolz.curried` versions of map and filter take the function up
# front, returning a one-argument callable that's perfect for `pipe`.
warm_fahrenheit = pipe(
    readings_c,
    map_c(to_fahrenheit),
    filter_c(is_above_freezing),
    sorted,
)

note("Above-freezing readings, in Fahrenheit, sorted:")
display(warm_fahrenheit, append=True)

heading("2. compose: build a reusable function from smaller ones")
note(
    "<code>compose(f, g)(x)</code> is <code>f(g(x))</code>. "
    "Useful when you want a named function rather than a one-shot pipe."
)

# A reusable cleaner: trim whitespace, lowercase, drop empty strings.
clean_tag = compose(str.lower, str.strip)
raw_tags = ["  Python ", "FUNCTIONAL", " toolz", "Python  ", "iterators"]
cleaned = list(cytoolz.unique(map(clean_tag, raw_tags)))

display({"cleaned, deduplicated tags": cleaned}, append=True)

heading("3. curry: partial application, the functional way")
note(
    "A curried function can be called with fewer arguments than it "
    "expects; it returns a new function waiting for the rest."
)


@curry
def scale_and_offset(scale, offset, x):
    """Apply y = scale * x + offset."""
    return scale * x + offset


# Pre-bake some specialized scalers by supplying the first arguments.
celsius_to_fahrenheit = scale_and_offset(9 / 5, 32)
double_then_add_one = scale_and_offset(2, 1)

display({
    "freezing in F":         celsius_to_fahrenheit(0),
    "body temp (37C) in F":  celsius_to_fahrenheit(37),
    "double_then_add_one(10)": double_then_add_one(10),
}, append=True)

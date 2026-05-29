# ---------------------------------------------------------------------
# functoolz: compose, pipe, curry, and memoize
# ---------------------------------------------------------------------

heading("Building a word-count pipeline with compose")
note(
    "<code>compose(f, g, h)</code> returns a function equivalent to "
    "<code>f(g(h(x)))</code>. Combined with curried <code>map</code> "
    "you get a tidy data pipeline."
)


def stem(word):
    """Strip punctuation and lowercase a word."""
    return word.lower().rstrip(",.!:;'-\"").lstrip("'\"")


# `map(stem)` is a curried map: it returns a function expecting an iterable.
wordcount = compose(frequencies, map(stem), str.split)

sentence = (
    "This cat jumped over this OTHER cat! "
    "That cat watched, unimpressed."
)
note(f"Input: <em>{sentence}</em>")
display(wordcount(sentence), append=True)

heading("pipe: the same idea, read left-to-right")
note(
    "<code>pipe(value, f, g, h)</code> threads a value through a "
    "sequence of functions. It often reads more naturally than "
    "<code>compose</code>."
)

# Take the five most common stems from a longer passage.
passage = (
    "the quick brown fox jumps over the lazy dog. "
    "the dog was not amused. the fox, however, was delighted."
)

top_five = pipe(
    passage,
    str.split,
    map(stem),
    filter(lambda w: len(w) > 2),
    frequencies,
    lambda d: sorted(d.items(), key=lambda kv: -kv[1]),
    take(5),
    list,
)
display(top_five, append=True)

heading("memoize: cache a slow pure function")
note(
    "<code>memoize</code> wraps a function so repeated calls with "
    "the same arguments return a cached result. Great for recursive "
    "definitions like Fibonacci."
)

call_count = {"n": 0}


@memoize
def fib(n):
    call_count["n"] += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


values = [fib(n) for n in range(15)]
note(f"First 15 Fibonacci numbers: {values}")
note(f"Underlying function calls made: <strong>{call_count['n']}</strong> "
     f"(without memoization this would be exponential).")

# ---------------------------------------------------------------------
# Section 2: Decorator factories that accept their own arguments.
# ---------------------------------------------------------------------

heading("2. Parameterised decorators: retry on failure")
note(
    "A common pattern: a decorator that takes configuration "
    "(how many attempts, which exceptions to catch). With "
    "`@decorator`, extra parameters become keyword arguments "
    "of the decorating function itself."
)


@decorator
def retry(func, attempts=3, exceptions=(Exception,), *args, **kw):
    """Retry `func` up to `attempts` times if it raises `exceptions`."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            result = func(*args, **kw)
            note(f"<code>{func.__name__}</code> succeeded on attempt {attempt}")
            return result
        except exceptions as exc:
            last_error = exc
            note(
                f"Attempt {attempt}/{attempts} of "
                f"<code>{func.__name__}</code> raised "
                f"<code>{type(exc).__name__}: {exc}</code>"
            )
    raise last_error


# A flaky function that fails the first two times it's called.
class FlakyService:
    def __init__(self, fail_count):
        self.fail_count = fail_count
        self.calls = 0

    @retry(attempts=4, exceptions=(ConnectionError,))
    def fetch(self, resource):
        """Pretend to fetch a remote resource."""
        self.calls += 1
        if self.calls <= self.fail_count:
            raise ConnectionError("network hiccup")
        return f"payload for {resource!r} (call #{self.calls})"


service = FlakyService(fail_count=2)
result = service.fetch("/api/widgets")

heading("Result")
display(result, append=True)

heading("Signature is still preserved")
note(
    f"<code>FlakyService.fetch{inspect.signature(FlakyService.fetch)}</code> "
    "— note that `self` and `resource` are still visible to introspection."
)

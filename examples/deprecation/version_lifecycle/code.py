# ---------------------------------------------------------------------
# Walking a function through the deprecation lifecycle.
# ---------------------------------------------------------------------
#
# `deprecation` raises different warning classes depending on where
# `current_version` sits relative to `deprecated_in` and `removed_in`:
#
#   * before `deprecated_in`         -> no warning yet (pre-deprecation)
#   * `deprecated_in` <= v < removed_in -> DeprecatedWarning
#   * v >= `removed_in`              -> UnsupportedWarning
#
# We demonstrate by re-decorating the same function at three different
# pretend "current versions" of our library.

heading("Walking through the deprecation lifecycle")


def make_decorated(current_version):
    """Return `legacy_greet` decorated as if our library were at this version."""

    @deprecation.deprecated(
        deprecated_in="1.5",
        removed_in="2.0",
        current_version=current_version,
        details="Use `greet` instead.",
    )
    def legacy_greet(name):
        return f"Hello, {name}!"

    return legacy_greet


def call_and_report(label, func, arg):
    """Call `func`, capture any warnings, and report them as HTML."""
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        result = func(arg)
    if not captured:
        note(f"<strong>{label}:</strong> no warning. Result: {result!r}")
        return
    for w in captured:
        note(
            f"<strong>{label}:</strong> "
            f"<code>{w.category.__name__}</code> &mdash; {w.message}"
        )


# Stage 1: we're still on 1.4, before the function was deprecated.
call_and_report("v1.4 (pre-deprecation)", make_decorated("1.4"), "Ada")

# Stage 2: we've shipped 1.7. The function is deprecated but still
# supported, so callers get a DeprecatedWarning.
call_and_report("v1.7 (deprecated)", make_decorated("1.7"), "Ada")

# Stage 3: we've shipped 2.0. The function should have been removed,
# so callers now get an UnsupportedWarning. This is the cue that
# `@fail_if_not_removed` watches for in your test suite -- it turns
# this warning into a failing assertion so the dead code can't
# linger forever.
call_and_report("v2.0 (should be removed)", make_decorated("2.0"), "Ada")

heading("Catching unsupported code in tests")
note(
    "Pair `@deprecation.deprecated` with "
    "<code>@deprecation.fail_if_not_removed</code> on your test methods. "
    "Once `current_version` reaches `removed_in`, the test fails with an "
    "<code>AssertionError</code>, reminding you to delete the deprecated "
    "code rather than letting it live forever."
)

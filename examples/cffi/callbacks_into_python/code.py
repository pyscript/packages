# ---------------------------------------------------------------------
# Callbacks: turning Python functions into C function pointers
# ---------------------------------------------------------------------
#
# Many C APIs take a function pointer -- think `qsort`, GUI event
# handlers, or signal callbacks. cffi's `ffi.callback(...)` wraps a
# Python function so that C can call it as if it were a C function.

ffi = FFI()

# qsort's signature, plus the comparator type it expects.
ffi.cdef("""
    typedef int (*compare_fn)(const void *, const void *);
    void qsort(void *base, size_t nmemb, size_t size, compare_fn cmp);
""")
libc = ffi.dlopen(None)

heading("Sorting a C array with a Python-defined comparator")

# Build a C array of ints to sort in place.
values = [42, 7, 19, -3, 256, 0, 88, 11]
buf = ffi.new("int[]", values)
note(f"Before qsort: {list(buf)}")

# `@ffi.callback(...)` turns a Python function into something C can call.
# The signature string mirrors the C typedef above.
@ffi.callback("int(const void *, const void *)")
def ascending(a, b):
    # a and b are `const void *`. Cast them to `int *` to read the values.
    ai = ffi.cast("int *", a)[0]
    bi = ffi.cast("int *", b)[0]
    return (ai > bi) - (ai < bi)

# Hand the callback to qsort. C calls back into Python once per compare.
libc.qsort(buf, len(buf), ffi.sizeof("int"), ascending)
note(f"After qsort ascending: {list(buf)}")

# Swap in a different Python comparator without recompiling anything.
@ffi.callback("int(const void *, const void *)")
def by_absolute_value(a, b):
    ai = abs(ffi.cast("int *", a)[0])
    bi = abs(ffi.cast("int *", b)[0])
    return (ai > bi) - (ai < bi)

libc.qsort(buf, len(buf), ffi.sizeof("int"), by_absolute_value)
note(f"After qsort by |value|: {list(buf)}")

note(
    "Keep a reference to the callback object alive for as long as C "
    "might call it -- once it's garbage collected, the C function "
    "pointer becomes invalid. For long-lived callbacks, see "
    "<code>extern \"Python\"</code> in the cffi docs: "
    "<a href='https://cffi.readthedocs.io/'>cffi.readthedocs.io</a>."
)

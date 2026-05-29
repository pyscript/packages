"""
A first taste of cffi: the Foreign Function Interface for Python
calling C code.

CFFI lets you describe a C API in plain C-ish syntax via `ffi.cdef(...)`,
then either:
  * load a shared library and call into it directly (ABI mode), or
  * compile a small extension that wraps a C library (API mode).

In this PyScript environment we'll use ABI mode (`ffi.dlopen`) to call
into the C standard library that's already loaded in the runtime.

Docs: https://cffi.readthedocs.io/
"""
from IPython.core.display import display, HTML

# Step 1: create an FFI instance. This is the entry point for everything.
ffi = FFI()

# Step 2: declare the C functions and types you want to use, in C syntax.
# CFFI doesn't need a real header file -- you just paste in what you need.
ffi.cdef("""
    int    abs(int x);
    double sqrt(double x);
    size_t strlen(const char *s);
""")

# Step 3: load the library that provides those symbols. Passing None
# means "the current process / standard C library".
libc = ffi.dlopen(None)

heading("Calling C functions from Python")
note("Each call below crosses the Python/C boundary via cffi.")

# Integers and floats convert to/from Python automatically.
display(HTML(f"<code>abs(-42)</code> &rarr; <b>{libc.abs(-42)}</b>"), append=True)
display(HTML(f"<code>sqrt(2.0)</code> &rarr; <b>{libc.sqrt(2.0):.6f}</b>"), append=True)

# Python str must be encoded to bytes to be passed as `const char *`.
greeting = b"hello, cffi"
length = libc.strlen(greeting)
display(
    HTML(f"<code>strlen({greeting!r})</code> &rarr; <b>{length}</b>"),
    append=True,
)

note(
    "Notice the pattern: declare the C signature once with "
    "<code>ffi.cdef</code>, then call the functions as if they were "
    "regular Python functions on the <code>lib</code> object."
)

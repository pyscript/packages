# ---------------------------------------------------------------------
# Allocating real C memory from Python with ffi.new(...)
# ---------------------------------------------------------------------
#
# Beyond calling functions, cffi lets you build C-level data: arrays,
# structs, and pointers. The values you create with `ffi.new(...)` are
# real C memory, garbage-collected when the Python handle goes away.

from cffi import FFI


ffi = FFI()

# Declare a struct type and a couple of helpers we'll use below.
ffi.cdef("""
    typedef struct {
        int   id;
        float temperature;
    } reading_t;

    int    abs(int x);
    size_t strlen(const char *s);
""")
libc = ffi.dlopen(None)

heading("1. A C array of ints")

# ffi.new("int[5]") allocates a zeroed C array of 5 ints. The result
# behaves like a Python sequence: index it, slice it, take its len().
counts = ffi.new("int[5]")
for i in range(5):
    counts[i] = (i + 1) ** 2
note(f"counts[:] = {list(counts)}, sizeof = {ffi.sizeof(counts)} bytes")

# You can also initialize from a Python list in one step.
primes = ffi.new("int[]", [2, 3, 5, 7, 11, 13])
note(f"primes has length {len(primes)}; primes[3] = {primes[3]}")

heading("2. A struct, allocated and initialized")

# ffi.new("reading_t *") gives a pointer to a fresh, zeroed struct.
# Like in C, you access fields via `->`-style dot access on the pointer.
sample = ffi.new("reading_t *", {"id": 7, "temperature": 21.5})
note(
    f"sample.id = {sample.id}, "
    f"sample.temperature = {sample.temperature:.2f}&deg;C"
)

heading("3. Strings: ffi.new('char[]') and ffi.string()")

# Build a writable C string buffer from Python bytes.
buf = ffi.new("char[]", b"weather station")
# Pass it to a C function expecting `const char *`.
note(f"strlen(buf) reported by libc: <b>{libc.strlen(buf)}</b>")
# Convert C bytes back to a Python bytes object.
note(f"ffi.string(buf) = {ffi.string(buf)!r}")

heading("4. Casting and addresses")

# ffi.cast lets you reinterpret values across compatible C types.
big_negative = ffi.cast("int", -123)
note(f"abs({int(big_negative)}) = {libc.abs(big_negative)}")

# ffi.addressof gives you a pointer to an existing cdata object.
sample_ptr = ffi.addressof(sample[0])
note(
    f"sample_ptr is a {ffi.typeof(sample_ptr).cname}; "
    f"it points at id={sample_ptr.id}."
)

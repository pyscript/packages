"""
A first look at `bitarray`: an efficient array-of-booleans type that
behaves much like a Python list, but packs eight bits into a byte.

See https://github.com/ilanschnell/bitarray for full documentation.
"""
from IPython.core.display import display, HTML
from bitarray import bitarray
from bitarray.util import ba2int, int2ba, ba2hex, hex2ba

heading("Building bitarrays")
note(
    "You can construct a bitarray from a string of 0s and 1s "
    "(whitespace and underscores are ignored), from an iterable "
    "of booleans, or as a fixed-length zero-filled buffer."
)

flags = bitarray("1011 0010 1110_0001")  # initialize from string
zeros = bitarray(16)                      # 16 zero bits
zeros.setall(0)
mixed = bitarray([1, 0, 0, 1, 1, 0, 1, 1])

note(f"flags = {flags!r} (length {len(flags)})")
note(f"zeros = {zeros!r}")
note(f"mixed = {mixed!r}")

heading("List-like behavior")
note(
    "Indexing a single position returns 0 or 1; slicing returns "
    "another bitarray. Slice assignment, append, and extend all "
    "work just like a list."
)

note(f"flags[0]    = {flags[0]} (a plain int)")
note(f"flags[0:4]  = {flags[0:4]!r} (a bitarray)")
note(f"flags.count(1) = {flags.count(1)} ones out of {len(flags)} bits")

flags.append(1)
flags.extend([0, 0, 1])
note(f"After append/extend: {flags!r}")

heading("Conversions: integers and hex")
note(
    "The `bitarray.util` module converts to and from common "
    "representations. The bit-endianness affects how those bits "
    "map to integer or hex values."
)

n = 0xCAFE
ba = int2ba(n, length=16)              # 16-bit big-endian by default
note(f"int2ba(0xCAFE, length=16) -> {ba!r}")
note(f"ba2hex(...) -> {ba2hex(ba)!r}, ba2int(...) -> {ba2int(ba)}")

# Round-trip from a hex string of arbitrary length.
roundtrip = hex2ba("deadbeef")
note(f"hex2ba('deadbeef') -> {roundtrip!r} ({len(roundtrip)} bits)")

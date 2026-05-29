"""
A first look at argon2-cffi: hashing a password and verifying it later.

Argon2 is a modern, memory-hard password hashing algorithm and the winner
of the Password Hashing Competition. The high-level entry point is
`PasswordHasher`, which picks sensible defaults for you.

Docs: https://argon2-cffi.readthedocs.io/
"""
from IPython.core.display import display, HTML

# A PasswordHasher with library-recommended defaults. You can tune
# memory cost, time cost, and parallelism, but the defaults are a fine
# starting point for most applications.
hasher = PasswordHasher()

heading("1. Hashing a password")
note(
    "Calling <code>hash()</code> returns a self-describing string that "
    "encodes the algorithm, parameters, salt, and digest. You store "
    "this whole string in your user database -- there is no separate "
    "salt column to manage."
)

password = "correct horse battery staple"
stored_hash = hasher.hash(password)

display(HTML(f"<pre>{stored_hash}</pre>"), append=True)

note(
    "Notice the prefix <code>$argon2id$</code> and the parameters "
    "<code>m=</code> (memory in KiB), <code>t=</code> (iterations), "
    "and <code>p=</code> (parallelism). Each call uses a fresh random "
    "salt, so hashing the same password twice produces different output."
)

second_hash = hasher.hash(password)
display(HTML(f"<pre>{second_hash}</pre>"), append=True)

heading("2. Verifying a login attempt")
note(
    "Use <code>verify()</code> to check a candidate password against a "
    "stored hash. It returns <code>True</code> on success and raises "
    "an exception on mismatch -- so your code can't accidentally treat "
    "a falsy return as success."
)

ok = hasher.verify(stored_hash, "correct horse battery staple")
note(f"Correct password verified: <strong>{ok}</strong>")

try:
    hasher.verify(stored_hash, "hunter2")
except VerifyMismatchError as exc:
    note(f"Wrong password raises: <code>{type(exc).__name__}</code>")

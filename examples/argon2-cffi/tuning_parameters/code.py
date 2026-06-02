# ---------------------------------------------------------------------
# Tuning Argon2's cost parameters and reading what's inside a hash.
# ---------------------------------------------------------------------

heading("Cost parameters: tradeoffs between security and speed")
note(
    "Argon2 has three knobs: <code>memory_cost</code> (KiB of RAM per "
    "hash), <code>time_cost</code> (iteration count), and "
    "<code>parallelism</code> (lanes). Higher values make brute-force "
    "attacks more expensive, but also slow down legitimate logins. "
    "Pick values that take a comfortable fraction of a second on your "
    "production hardware."
)

password = "correct horse battery staple"

# A few configurations spanning "fast" to "stronger". The numbers
# are illustrative; tune for your own environment. Inside a browser the
# parallelism must only be set to 1. In regular Python this value can be
# higher.
configurations = [
    ("fast",     {"memory_cost": 8 * 1024,  "time_cost": 1, "parallelism": 1}),
    ("default",  {"memory_cost": 64 * 1024, "time_cost": 3, "parallelism": 1}),
    ("stronger", {"memory_cost": 128 * 1024, "time_cost": 4, "parallelism": 1}),
]

rows = ["<tr><th>Profile</th><th>memory_cost (KiB)</th>"
        "<th>time_cost</th><th>parallelism</th><th>hash time (ms)</th></tr>"]

for label, params in configurations:
    hasher = PasswordHasher(**params)
    start = time.perf_counter()
    hasher.hash(password)
    elapsed_ms = (time.perf_counter() - start) * 1000
    rows.append(
        f"<tr><td>{label}</td>"
        f"<td>{params['memory_cost']}</td>"
        f"<td>{params['time_cost']}</td>"
        f"<td>{params['parallelism']}</td>"
        f"<td>{elapsed_ms:.1f}</td></tr>"
    )

display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

heading("Migrating old hashes with check_needs_rehash")
note(
    "When you raise your cost parameters, existing hashes in your "
    "database become weaker than your new policy. After a successful "
    "login, call <code>check_needs_rehash()</code>: if it returns "
    "<code>True</code>, re-hash the password and store the new value. "
    "This lets you upgrade silently as users log in."
)

# Simulate a hash created long ago with weak parameters.
old_hasher = PasswordHasher(memory_cost=8 * 1024, time_cost=1, parallelism=1)
old_hash = old_hasher.hash(password)

# Today's policy is stronger.
current_hasher = PasswordHasher(
    memory_cost=64 * 1024, time_cost=3, parallelism=1,
)

assert current_hasher.verify(old_hash, password)
needs_rehash = current_hasher.check_needs_rehash(old_hash)
note(f"Old hash needs rehash under current policy: <strong>{needs_rehash}</strong>")

if needs_rehash:
    upgraded = current_hasher.hash(password)
    note("Upgraded hash (store this in place of the old one):")
    display(HTML(f"<pre>{upgraded}</pre>"), append=True)
    note(
        f"Still needs rehash? "
        f"<strong>{current_hasher.check_needs_rehash(upgraded)}</strong>"
    )

heading("Choosing the Argon2 variant")
note(
    "Argon2 comes in three variants: <code>Type.I</code> (side-channel "
    "resistant), <code>Type.D</code> (GPU-attack resistant), and "
    "<code>Type.ID</code> (hybrid, the recommended default). You "
    "rarely need to change this, but it's a one-liner if you do."
)

id_hasher = PasswordHasher(type=Type.ID)
sample = id_hasher.hash(password)
note(f"Variant prefix: <code>{sample.split('$')[1]}</code>")

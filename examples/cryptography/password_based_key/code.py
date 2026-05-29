# ---------------------------------------------------------------------
# Section 2: Turning a human password into a Fernet key with PBKDF2.
# ---------------------------------------------------------------------

heading("2. Password-based encryption with PBKDF2HMAC")
note(
    "Humans pick passwords; Fernet wants 32 random bytes. A key "
    "derivation function (KDF) bridges the gap. PBKDF2 stretches "
    "a password with many hash iterations and a random salt, "
    "making brute-force attacks expensive."
)

password = b"correct horse battery staple"
salt = os.urandom(16)  # store alongside the ciphertext; not secret.

# 480,000 iterations is a reasonable default for SHA-256 PBKDF2.
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480_000,
)
derived_key = base64.urlsafe_b64encode(kdf.derive(password))

note("Salt (random, store with the ciphertext):")
display(HTML(f"<code>{salt.hex()}</code>"), append=True)
note("Derived Fernet-compatible key:")
display(HTML(f"<code>{derived_key.decode()}</code>"), append=True)

cipher = Fernet(derived_key)
token = cipher.encrypt(b"Treasure buried beneath the old oak tree.")
note("Encrypted with the password-derived key:")
display(HTML(f"<code style='word-break:break-all'>{token.decode()}</code>"), append=True)

# To decrypt later, re-derive the key from the same password and salt.
kdf_again = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480_000,
)
rederived = base64.urlsafe_b64encode(kdf_again.derive(password))
note(f"Decrypted: <strong>{Fernet(rederived).decrypt(token).decode()}</strong>")

# A wrong password produces a different key, and Fernet refuses to decrypt.
heading("Wrong password is rejected", level=3)
wrong_kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000,
)
wrong_key = base64.urlsafe_b64encode(wrong_kdf.derive(b"hunter2"))
try:
    Fernet(wrong_key).decrypt(token)
except InvalidToken:
    note("Caught <code>InvalidToken</code>: wrong password, no plaintext. ✅")

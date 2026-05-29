# ---------------------------------------------------------------------
# Real systems rarely keep RSA keys in memory only: keys get saved
# to disk, sent across networks, or pasted into config files. The
# standard interchange format is PEM (Base64-wrapped DER). The
# `rsa` package can serialize keys to PEM bytes and parse them
# back, no files required.
# ---------------------------------------------------------------------

heading("1. Generate a key pair and serialize both halves to PEM")

public_key, private_key = rsa.newkeys(512)

public_pem = public_key.save_pkcs1(format="PEM")
private_pem = private_key.save_pkcs1(format="PEM")

note("Public key in PEM form (this is what you'd share):")
display(HTML(f"<pre>{public_pem.decode()}</pre>"), append=True)

note("Private key in PEM form (this is what you'd protect):")
display(HTML(f"<pre>{private_pem.decode()}</pre>"), append=True)


heading("2. Load the keys back from their PEM bytes")
note(
    "The corresponding <code>load_pkcs1</code> classmethods turn "
    "PEM bytes back into key objects. The reloaded keys are "
    "equivalent to the originals."
)

reloaded_public = rsa.PublicKey.load_pkcs1(public_pem)
reloaded_private = rsa.PrivateKey.load_pkcs1(private_pem)

note(f"Public keys match: <strong>{reloaded_public == public_key}</strong>")
note(
    f"Private keys match: "
    f"<strong>{reloaded_private == private_key}</strong>"
)


heading("3. Use the reloaded keys end-to-end")
note(
    "To prove the reloaded keys really work, we encrypt with the "
    "reloaded public key and decrypt with the reloaded private "
    "key, just as if they had come from a file on disk."
)

secret = b"The PEM round-trip preserves everything we need."
ciphertext = rsa.encrypt(secret, reloaded_public)
recovered = rsa.decrypt(ciphertext, reloaded_private)

note(f"Original: <code>{secret.decode()}</code>")
note(f"Recovered: <code>{recovered.decode()}</code>")
note(
    f"Round-trip through PEM succeeded: "
    f"<strong>{recovered == secret}</strong>"
)

"""
A first look at the `rsa` package: a pure-Python implementation of
RSA public-key cryptography (PKCS#1 v1.5).

Here we'll generate a fresh key pair, encrypt a short message with
the public key, and decrypt it again with the matching private key.
This is the classic "send a secret to someone" workflow: anyone with
the public key can encrypt, but only the holder of the private key
can decrypt.

Docs: https://stuvel.eu/python-rsa-doc/
"""
from IPython.core.display import display, HTML

import rsa


heading("1. Generate a fresh RSA key pair")
note(
    "We use a small 512-bit key here so it generates quickly in the "
    "browser. For real applications use at least 2048 bits! "
    "<code>rsa.newkeys</code> returns a (public_key, private_key) "
    "tuple."
)

public_key, private_key = rsa.newkeys(512)

note("The public key (safe to share):")
display(HTML(f"<pre>{public_key}</pre>"), append=True)

note("The private key (keep this secret!):")
display(HTML(f"<pre>{private_key}</pre>"), append=True)


heading("2. Encrypt a message with the public key")
note(
    "RSA operates on bytes, so we encode our string as UTF-8 before "
    "encrypting. The ciphertext is itself bytes; we show its length "
    "and a hex preview."
)

plaintext = "Meet me at the docks at midnight."
ciphertext = rsa.encrypt(plaintext.encode("utf-8"), public_key)

note(f"Plaintext: <code>{plaintext}</code>")
note(f"Ciphertext is {len(ciphertext)} bytes. First 32 bytes in hex:")
display(HTML(f"<pre>{ciphertext[:32].hex()}</pre>"), append=True)


heading("3. Decrypt with the private key")
note(
    "Only the holder of the private key can recover the original "
    "message. The result is bytes, which we decode back to a string."
)

recovered = rsa.decrypt(ciphertext, private_key).decode("utf-8")
note(f"Recovered plaintext: <code>{recovered}</code>")
note(f"Round-trip succeeded: <strong>{recovered == plaintext}</strong>")

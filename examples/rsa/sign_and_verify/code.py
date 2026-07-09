# ---------------------------------------------------------------------
# Signing answers a different question than encryption: not "can I
# keep this secret?" but "can the recipient prove it really came
# from me, untampered?". The signer uses their private key; anyone
# with the matching public key can verify.
# ---------------------------------------------------------------------

heading("1. Alice generates a key pair and signs a message")
note(
    "Alice will publish her public key so others can verify her "
    "signatures. She keeps her private key to herself."
)

alice_public, alice_private = rsa.newkeys(512)

message = b"I, Alice, authorize the transfer of 100 credits to Bob."
signature = rsa.sign(message, alice_private, "SHA-256")

note(f"Message: <code>{message.decode()}</code>")
note(
    f"Signature is {len(signature)} bytes. First 32 bytes in hex:"
)
display(HTML(f"<pre>{signature[:32].hex()}</pre>"), append=True)


heading("2. Bob verifies the signature with Alice's public key")
note(
    "<code>rsa.verify</code> returns the hash algorithm name on "
    "success and raises <code>rsa.VerificationError</code> on "
    "failure. We catch that to show both outcomes."
)

try:
    hash_used = rsa.verify(message, signature, alice_public)
    note(
        f"Signature is valid. Hashed using "
        f"<strong>{hash_used}</strong>."
    )
except rsa.VerificationError as exc:
    note(f"Signature failed to verify: {exc}")


heading("3. What happens if the message is tampered with?")
note(
    "If even a single byte of the message changes, verification "
    "must fail. Here we flip 'Bob' to 'Eve' and try to verify "
    "against the original signature."
)

tampered = message.replace(b"Bob", b"Eve")
note(f"Tampered message: <code>{tampered.decode()}</code>")

try:
    rsa.verify(tampered, signature, alice_public)
    note("Unexpectedly accepted the tampered message!")
except rsa.VerificationError as exc:
    note(
        f"Tampered message correctly rejected: "
        f"<strong>{exc}</strong>"
    )

# ---------------------------------------------------------------------
# Alice and Bob exchange messages using Curve25519 key pairs.
# ---------------------------------------------------------------------

heading("Alice and Bob exchange keys")
note(
    "Each party generates a private key and shares the matching "
    "public key. A Box built from <em>my private key</em> and "
    "<em>their public key</em> can encrypt to them and decrypt "
    "from them."
)

# Bob's long-term key pair.
bob_secret = PrivateKey.generate()
bob_public = bob_secret.public_key

# Alice's long-term key pair.
alice_secret = PrivateKey.generate()
alice_public = alice_secret.public_key

note(f"Bob's public key (hex): "
     f"<code>{bob_public.encode(HexEncoder).decode()}</code>")
note(f"Alice's public key (hex): "
     f"<code>{alice_public.encode(HexEncoder).decode()}</code>")

# Bob prepares a Box to send messages to Alice.
bob_to_alice = Box(bob_secret, alice_public)
encrypted = bob_to_alice.encrypt(b"Meet me by the old oak at midnight.")

note(f"Ciphertext length: {len(encrypted.ciphertext)} bytes")

# Alice opens the matching Box to read it.
alice_from_bob = Box(alice_secret, bob_public)
plaintext = alice_from_bob.decrypt(encrypted)
note(f"Alice reads: <strong>{plaintext.decode()}</strong>")

heading("Anonymous messages with SealedBox")
note(
    "A SealedBox lets anyone send a message to a recipient using "
    "only the recipient's public key. Each message uses a fresh "
    "ephemeral sender key that is destroyed after encryption, so "
    "even the sender cannot decrypt it later."
)

# Anyone holding Bob's public key can seal a message to him.
sealed = SealedBox(bob_public).encrypt(b"An anonymous tip for Bob.")
note(f"Sealed ciphertext length: {len(sealed)} bytes "
     f"(includes a 32-byte ephemeral public key)")

# Only Bob, with his private key, can unseal it.
unsealed = SealedBox(bob_secret).decrypt(sealed)
note(f"Bob unseals: <strong>{unsealed.decode()}</strong>")

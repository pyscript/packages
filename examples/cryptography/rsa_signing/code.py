# ---------------------------------------------------------------------
# Section 3: Asymmetric crypto: signing a message with RSA.
# ---------------------------------------------------------------------
# Package imports for this example.
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


heading("3. RSA: generating keys, signing, and verifying")
note(
    "Asymmetric crypto uses a key pair: the <em>private</em> key signs, "
    "the <em>public</em> key verifies. We'll generate a 2048-bit RSA "
    "keypair, sign a release note, and confirm a verifier can detect "
    "tampering."
)

# Generate a fresh RSA keypair. 2048 bits is the modern minimum.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Serialize the public key to PEM so it can be shared.
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
note("Public key (PEM, safe to share):")
display(HTML(f"<pre style='font-size:0.85em'>{public_pem.decode()}</pre>"), append=True)

message = b"Release v1.4.2 ships at midnight. Approved by Alice."

# Sign with PSS padding and SHA-256, the modern recommendation.
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)
note(f"Signature length: <strong>{len(signature)} bytes</strong> (first 16 in hex):")
display(HTML(f"<code>{signature[:16].hex()}…</code>"), append=True)

# A verifier loads the public key from PEM and checks the signature.
verifier_key = serialization.load_pem_public_key(public_pem)


def verify(msg, sig):
    try:
        verifier_key.verify(
            sig, msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


heading("Verification", level=3)
note(f"Original message verifies: <strong>{verify(message, signature)}</strong> ✅")

tampered = message.replace(b"Alice", b"Eve  ")
note(f"Tampered message verifies: <strong>{verify(tampered, signature)}</strong> ❌")
note(
    "The signature is bound to the exact bytes that were signed. "
    "Any change — even swapping a name — invalidates it."
)

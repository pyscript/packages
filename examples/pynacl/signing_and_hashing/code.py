# ---------------------------------------------------------------------
# Ed25519 digital signatures: prove who wrote a message.
# ---------------------------------------------------------------------

import nacl.hash
import nacl.pwhash
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError, InvalidkeyError


heading("Signing a release announcement")
note(
    "A SigningKey produces signatures; the matching VerifyKey "
    "checks them. Anyone with the verify key can confirm the "
    "message came from the signer and was not modified."
)

signing_key = SigningKey.generate()
verify_key = signing_key.verify_key

note(f"Verify key (hex): "
     f"<code>{verify_key.encode(HexEncoder).decode()}</code>")

announcement = b"Version 2.0 is out. Download from the official site."
signed = signing_key.sign(announcement)

note(f"Signed bundle length: {len(signed)} bytes "
     f"(64-byte signature + {len(announcement)}-byte message)")

# Verification returns the original message, or raises on tampering.
verified_message = verify_key.verify(signed)
note(f"Verified message: <strong>{verified_message.decode()}</strong>")

# Demonstrate detection of a forgery.
forged = signed[:-1] + bytes([signed[-1] ^ 0x01])
try:
    verify_key.verify(forged)
except BadSignatureError as exc:
    note(f"Forgery rejected: <code>BadSignatureError</code>: {exc}")

# ---------------------------------------------------------------------
# Hashing a message with BLAKE2b.
# ---------------------------------------------------------------------

heading("Fingerprinting data with BLAKE2b")
note(
    "nacl.hash.blake2b produces a fast, keyed cryptographic hash. "
    "Useful for deduplication, integrity checks, or building MACs."
)

digest = nacl.hash.blake2b(announcement, encoder=HexEncoder)
note(f"BLAKE2b(announcement) = <code>{digest.decode()}</code>")

# ---------------------------------------------------------------------
# Password hashing with Argon2id.
# ---------------------------------------------------------------------

heading("Storing passwords safely with Argon2id")
note(
    "Never store raw passwords. nacl.pwhash.argon2id.str() returns "
    "a self-contained verifier string with a random salt and tunable "
    "cost parameters baked in. Use INTERACTIVE limits for login "
    "flows; SENSITIVE limits for high-value secrets."
)

password = b"correct horse battery staple"

# Use INTERACTIVE limits so the demo runs quickly in the browser.
verifier = nacl.pwhash.argon2id.str(
    password,
    opslimit=nacl.pwhash.argon2id.OPSLIMIT_INTERACTIVE,
    memlimit=nacl.pwhash.argon2id.MEMLIMIT_INTERACTIVE,
)
note(f"Stored verifier: <code>{verifier.decode()}</code>")

# Successful verification returns True.
ok = nacl.pwhash.verify(verifier, password)
note(f"Correct password verifies: <strong>{ok}</strong>")

# A wrong password raises InvalidkeyError.
try:
    nacl.pwhash.verify(verifier, b"hunter2")
except InvalidkeyError as exc:
    note(f"Wrong password rejected: <code>InvalidkeyError</code>: {exc}")

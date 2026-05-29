"""
A first taste of PyNaCl: symmetric (secret-key) encryption.

Two parties who already share a secret key can use SecretBox to
exchange confidential, authenticated messages. The ciphertext is
sealed with a 16-byte authenticator: any tampering causes
decryption to fail loudly.

Docs: https://pynacl.readthedocs.io/en/latest/secret/
"""
from IPython.core.display import display, HTML

heading("A diary entry, locked with a shared key")
note(
    "We generate a random 32-byte key, encrypt a short message, "
    "and then decrypt it again. The same key is used for both "
    "operations, so it must be kept secret."
)

# A SecretBox key is exactly 32 random bytes.
key = nacl.utils.random(SecretBox.KEY_SIZE)
box = SecretBox(key)

message = b"Dear diary: today I learned about libsodium."

# When the nonce is omitted, PyNaCl picks a fresh random one.
# A nonce must NEVER be reused with the same key.
encrypted = box.encrypt(message)

note(f"Key (hex): <code>{key.hex()}</code>")
note(f"Plaintext length: {len(message)} bytes")
note(f"Ciphertext length: {len(encrypted.ciphertext)} bytes "
     f"(plaintext + 16-byte authenticator)")
note(f"Nonce (hex): <code>{encrypted.nonce.hex()}</code>")

# The EncryptedMessage carries both the nonce and the ciphertext,
# so we can pass it straight back into decrypt().
plaintext = box.decrypt(encrypted)
note(f"Decrypted message: <strong>{plaintext.decode()}</strong>")

heading("Tampering is detected")
note(
    "If anyone flips a single bit of the ciphertext, decryption "
    "raises a CryptoError instead of returning garbage."
)

from nacl.exceptions import CryptoError

# Flip one byte of the ciphertext to simulate tampering.
tampered = bytearray(encrypted)
tampered[-1] ^= 0x01
try:
    box.decrypt(bytes(tampered))
except CryptoError as exc:
    note(f"Caught <code>CryptoError</code>: {exc}")

"""
A first look at `cryptography`: encrypting a secret note.

Fernet is the package's high-level "just give me safe symmetric
encryption" recipe. It uses AES-128 in CBC mode with HMAC-SHA256
for authentication, with all the bookkeeping (IVs, padding, MAC
verification) handled for you.

Docs: https://cryptography.io/en/latest/fernet/
"""
from IPython.core.display import display, HTML

# Package imports for this example.
from cryptography.fernet import Fernet, InvalidToken


heading("1. Encrypting a secret note with Fernet")
note(
    "Imagine you want to stash a private journal entry in local "
    "storage. Fernet gives you an authenticated, URL-safe token."
)

# A Fernet key is 32 random bytes, base64-encoded. Generate once,
# then keep it somewhere safe (a vault, a config file, etc.).
key = Fernet.generate_key()
cipher = Fernet(key)

journal_entry = b"Dear diary: today I learned about authenticated encryption."
token = cipher.encrypt(journal_entry)

note("The generated key (keep this secret!):")
display(HTML(f"<code>{key.decode()}</code>"), append=True)

note("The encrypted token (safe to store or transmit):")
display(HTML(f"<code style='word-break:break-all'>{token.decode()}</code>"), append=True)

# Decrypting with the same key recovers the original bytes.
recovered = cipher.decrypt(token)
note(f"Decrypted message: <strong>{recovered.decode()}</strong>")

heading("Tampering is detected", level=3)
note(
    "Fernet tokens are authenticated. Flip a single character and "
    "decryption raises <code>InvalidToken</code> rather than returning "
    "garbage."
)

tampered = token[:-4] + b"AAAA"
try:
    cipher.decrypt(tampered)
except InvalidToken:
    note("Caught <code>InvalidToken</code>: the tampered token was rejected. ✅")

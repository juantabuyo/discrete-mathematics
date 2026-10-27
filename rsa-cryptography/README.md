# RSA cryptography

We used the modular arithmetic library from our first assignment to implement RSA in a two-person Discrete Mathematics project at ICAI. It covers key generation, Unicode encoding, encryption, decryption and decimal padding. Two attacks show how small moduli can be factored and how unpadded character ciphertexts can be matched using a public key.

The registration and chat scripts exchange messages locally: ciphertext integers are copied between terminals. There is no network connection or messaging service.

## Run an example

Checked with Python 3.12.2 on macOS and Python 3.12.14. The application uses only the standard library. Run from this folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python - <<'PYCODE'
from rsa import encrypt_text, decrypt_text, recover_private_exponent

# Public teaching values, unsuitable for protecting real messages.
n, e, d = 3233, 17, 2753
ciphertext = encrypt_text("Hello", n, e, 0)
print(ciphertext)
print(decrypt_text(ciphertext, n, d, 0))
print(recover_private_exponent(n, e) == d)
PYCODE
```

Output from this public teaching example:

```text
[3000, 1313, 745, 745, 2185]
Hello
True
```

Each integer encrypts one character. Decryption restores the text, and the final line confirms that factoring the small modulus recovers the supplied private exponent. On Windows, activate with `.venv\Scripts\activate`.

For the interactive exercise, run `python register_user.py` twice. Use fictitious aliases `demo_alice` and `demo_bob`, prime bounds `100` and `200`, and `1` padding digit. This creates teaching key files in `keys/` beside the scripts. Registering an existing alias replaces its files.

```bash
python local_chat.py demo_alice demo_bob
```

Choose `E` to encrypt, `D` to decrypt and `Q` to quit. In another terminal, reverse the aliases to receive the first user's message. Generated keys are excluded by `.gitignore`.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```

The original 82 tests passed with pytest 9.1.1 on Python 3.12.2 (macOS) and Python 3.12.14. The public teaching example above also ran on macOS, including decryption and recovery of the small private exponent. Tests cover key generation, padding, Unicode, both attacks and a complete local chat round trip using temporary teaching keys. Modular exponentiation is checked against Python's `pow`.

## How it works

`rsa.py` chooses two distinct primes, computes the modulus and totient, then finds an invertible public exponent and its modular inverse. Encryption and decryption call the repeated-squaring implementation in `modular.py`. `recover_private_exponent` factors a small modulus; `recover_unpadded_text` instead encrypts candidate Unicode characters with the public key and matches the results.

`register_user.py` writes the local teaching keys, while `local_chat.py` reads them and provides the terminal interface. The key files are deliberately simple so the mathematical steps remain visible.

## Limitations

This is educational textbook RSA, not secure encryption. It uses Python's `random`, per-character encryption, decimal padding rather than OAEP, and plaintext private-key files. Encryption rejects characters whose full padding range cannot fit below the modulus. Prime enumeration and trial division are intended for small examples.

The team implemented the algorithms and local scripts from coursework interfaces. Course tests are retained with English names. A local `modular.py` keeps the project independently runnable. Post-submission fixes cover key selection, padding, key recovery and file handling; the interface is now in English.

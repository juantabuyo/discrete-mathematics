"""Educational RSA, decimal padding and attacks on small or unpadded messages.

This is textbook RSA for coursework, not a secure encryption library.
The algorithms follow the coursework exercises.
"""

import random
from typing import List, Tuple

import modular


def generate_keys(minimum_prime: int, maximum_prime: int) -> Tuple[int, int, int]:
    """Return (n, e, d) using distinct primes in [minimum_prime, maximum_prime).

    Raise ValueError if the interval contains fewer than two primes. Prime
    selection uses Python's random module and is not cryptographically secure.
    """
    primes = modular.list_primes(minimum_prime, maximum_prime)
    if len(primes) < 2:
        raise ValueError("The interval must contain at least two distinct primes")
    p1, p2 = random.sample(primes, 2)
    n = p1 * p2
    phi_n = (p1 - 1) * (p2 - 1)

    # For the smallest pair (2, 3), e=3 is congruent to 1 modulo phi(n).
    e = 3
    for i in range(2, phi_n):
        if modular.coprime(i, phi_n):
            e = i
            break
    d = modular.modular_inverse(e, phi_n)
    return n, e, d


def add_padding(m: int, padding_digits: int) -> int:
    """Append random decimal digits to a non-negative integer.

    padding_digits must be non-negative. This decimal scheme is not OAEP.
    """
    if m < 0 or padding_digits < 0:
        raise ValueError("The message and padding length must be non-negative")
    digits = str(m)
    for _ in range(padding_digits):
        digits += str(random.randint(0, 9))
    return int(digits)


def remove_padding(m: int, padding_digits: int) -> int:
    """Remove the final decimal digits, including padding on an original zero."""
    if m < 0 or padding_digits < 0:
        raise ValueError("The message and padding length must be non-negative")
    return m // (10**padding_digits)


def encrypt_integer(m: int, n: int, e: int, padding_digits: int) -> int:
    """Pad and encrypt a non-negative integer with the public key (n, e).

    The full padding range must fit below n: (m + 1) * 10**padding <= n.
    Raise ValueError rather than silently reducing an oversized message.
    """
    if n <= 1 or e <= 0:
        raise ValueError("The modulus must exceed one and the exponent be positive")
    if m < 0 or padding_digits < 0:
        raise ValueError("The message and padding length must be non-negative")
    if (m + 1) * (10**padding_digits) > n:
        raise ValueError("The message and padding do not fit below the modulus")
    m_pad = add_padding(m, padding_digits)
    return modular.modular_power(m_pad, e, n)


def decrypt_integer(c: int, n: int, d: int, padding_digits: int) -> int:
    """Decrypt a ciphertext integer and remove its decimal padding."""
    if n <= 1 or d <= 0 or not 0 <= c < n or padding_digits < 0:
        raise ValueError("Invalid ciphertext, key or padding length")
    m_pad = modular.modular_power(c, d, n)
    return remove_padding(m_pad, padding_digits)


def encode_text(s: str) -> List[int]:
    """Return the Unicode code point of each character in s."""
    return [ord(c) for c in s]


def decode_text(m: List[int]) -> str:
    """Decode Unicode code points; raise ValueError for an out-of-range value."""
    return "".join(chr(x) for x in m)


def encrypt_text(s: str, n: int, e: int, padding_digits: int) -> List[int]:
    """Encrypt each character separately; every code point and padding must fit."""
    code_points = encode_text(s)
    return [encrypt_integer(m, n, e, padding_digits) for m in code_points]


def decrypt_text(ciphertexts: List[int], n: int, d: int, padding_digits: int) -> str:
    """Decrypt character ciphertexts and decode the resulting Unicode values."""
    code_points = [decrypt_integer(c, n, d, padding_digits) for c in ciphertexts]
    return decode_text(code_points)


def recover_private_exponent(n: int, e: int) -> int:
    """Recover d by factoring n to compute Euler's totient, then inverting e.

    This trial-division attack is intended for small teaching examples. Raise
    ValueError if no inverse exists; assume n is a valid RSA modulus.
    """
    if n <= 1 or e <= 0:
        raise ValueError("The modulus must exceed one and the exponent be positive")
    try:
        return modular.modular_inverse(e, modular.totient(n))
    except ZeroDivisionError as err:
        raise ValueError("The public exponent has no inverse modulo phi(n)") from err


def recover_unpadded_text(ciphertexts: List[int], n: int, e: int) -> str:
    """Recover unpadded character ciphertexts by encrypting possible characters.

    This public-key lookup attack does not factor n or recover a private key.
    It assumes a valid RSA key and code points below n. It searches Unicode
    values in ascending order and stops when all requested ciphertexts match.
    Raise ValueError if a ciphertext has no matching Unicode code point.
    """
    if n <= 1 or e <= 0 or any(not 0 <= c < n for c in ciphertexts):
        raise ValueError("Invalid public key or ciphertext")
    if not ciphertexts:
        return ""
    remaining = set(ciphertexts)
    characters = {}
    for m in range(min(n, 0x110000)):
        c = modular.modular_power(m, e, n)
        if c in remaining:
            characters[c] = chr(m)
            remaining.remove(c)
            if not remaining:
                return "".join(characters[c] for c in ciphertexts)
    raise ValueError("The ciphertext has no matching unpadded Unicode text")

"""Create local teaching key files for a fictitious chat user."""

from pathlib import Path
from typing import Tuple

import rsa

KEY_DIRECTORY = str(Path(__file__).resolve().parent / "keys")


def prompt_alias() -> str:
    while True:
        name = input("Enter a fictitious user alias: ").strip()
        if name and not any(c in name for c in ("/", "\\")):
            return name
        print("Use a non-empty alias without directory separators.")


def prompt_prime_bounds() -> Tuple[int, int]:
    while True:
        try:
            n1 = int(input("Minimum prime (inclusive): ").strip())
            n2 = int(input("Maximum prime (exclusive): ").strip())
        except ValueError:
            print("Enter valid integers.")
            continue
        if n1 < 2:
            print("The minimum must be at least 2.")
            continue
        if n1 >= n2:
            print("The maximum must be greater than the minimum.")
            continue
        return n1, n2


def prompt_padding() -> int:
    while True:
        try:
            padding = int(input("Number of decimal padding digits: ").strip())
        except ValueError:
            print("Enter an integer.")
            continue
        if padding < 0:
            print("The padding length must be non-negative.")
            continue
        return padding


def create_key_directory() -> None:
    Path(KEY_DIRECTORY).mkdir(parents=True, exist_ok=True)


def write_public_key(n: int, e: int, padding: int, name: str) -> None:
    """Write n, e and padding on separate lines in the public key file."""
    path = Path(KEY_DIRECTORY) / f"pub_{name}.txt"
    with open(path, "w", encoding="utf-8") as file:
        file.write(f"{n}\n{e}\n{padding}\n")


def write_private_key(d: int, name: str) -> None:
    """Write the private exponent as plaintext for this local exercise only."""
    path = Path(KEY_DIRECTORY) / f"priv_{name}.txt"
    with open(path, "w", encoding="utf-8") as file:
        file.write(f"{d}\n")


if __name__ == "__main__":
    try:
        name = prompt_alias()
        while True:
            minimum_prime, maximum_prime = prompt_prime_bounds()
            try:
                n, e, d = rsa.generate_keys(minimum_prime, maximum_prime)
                break
            except ValueError as err:
                print(err)
        padding = prompt_padding()
        create_key_directory()
        write_public_key(n, e, padding, name)
        write_private_key(d, name)
        print("Local teaching keys saved. Do not use them for real messages.")
    except (EOFError, KeyboardInterrupt):
        print("\nRegistration cancelled.")

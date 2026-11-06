"""Encrypt or decrypt messages locally using manually exchanged ciphertexts."""

import sys
from pathlib import Path
from typing import Tuple

import rsa
from register_user import KEY_DIRECTORY

KEY_PATH = Path(KEY_DIRECTORY)


def read_public_key(name: str) -> Tuple[int, int, int]:
    """Read n, e and padding from a user's local public key file."""
    path = KEY_PATH / f"pub_{name}.txt"
    try:
        lst = []
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                value = line.strip()
                if value:
                    try:
                        lst.append(int(value))
                    except ValueError as err:
                        raise ValueError(f"Non-numeric value in {path}") from err
                if len(lst) == 3:
                    break
        if len(lst) < 3:
            raise ValueError(f"Invalid format in {path}; expected n, e and padding")
        n, e, padding = lst
        return n, e, padding
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Public key file not found: {path}") from err


def read_private_key(name: str) -> int:
    """Read the private exponent from a local plaintext teaching key file."""
    path = KEY_PATH / f"priv_{name}.txt"
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                value = line.strip()
                if value:
                    try:
                        return int(value)
                    except ValueError as err:
                        raise ValueError(f"Non-numeric value in {path}") from err
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Private key file not found: {path}") from err
    raise ValueError(f"Invalid format in {path}; expected one line containing d")


def exit_with_usage():
    print("Usage: python local_chat.py <local_user> <other_user>")
    sys.exit(2)


def read_option() -> str:
    try:
        return input("Encrypt (E), decrypt (D) or quit (Q)? ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        return "Q"


def read_plaintext() -> str:
    return input("Plaintext to encrypt: ")


def read_ciphertext() -> list:
    text = input("Ciphertext integers, separated by spaces: ").strip()
    if not text:
        raise ValueError("The ciphertext is empty")
    try:
        return [int(x) for x in text.split()]
    except ValueError as err:
        raise ValueError("Enter integers separated by spaces") from err


def print_ciphertext(lst: list) -> None:
    print(" ".join(str(x) for x in lst))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit_with_usage()
    _, local_user, other_user = sys.argv
    try:
        n1, e1, padding1 = read_public_key(local_user)
        d1 = read_private_key(local_user)
        n2, e2, padding2 = read_public_key(other_user)
    except (FileNotFoundError, ValueError) as err:
        print(err)
        sys.exit(1)
    print("Local teaching keys loaded.")

    while True:
        option = read_option()
        if option == "Q":
            print("Exiting.")
            break
        elif option == "E":
            try:
                text = read_plaintext()
                ciphertext = rsa.encrypt_text(text, n2, e2, padding2)
                print_ciphertext(ciphertext)
            except (ValueError, ZeroDivisionError) as err:
                print(f"Encryption failed: {err}")
            except (EOFError, KeyboardInterrupt):
                break
        elif option == "D":
            try:
                lst = read_ciphertext()
                plaintext = rsa.decrypt_text(lst, n1, d1, padding1)
                print(plaintext)
            except (ValueError, ZeroDivisionError) as err:
                print(f"Decryption failed: {err}")
            except (EOFError, KeyboardInterrupt):
                break
        else:
            print("Unknown option.")

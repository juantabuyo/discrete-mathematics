"""Independent checks for key, padding, attack and local file handling errors."""

import builtins
import math

import local_chat
import pytest
import register_user
import rsa


@pytest.mark.parametrize("lower,upper", [(0, 2), (2, 3), (14, 17), (20, 10)])
def test_key_generation_requires_two_primes(lower, upper):
    with pytest.raises(ValueError):
        rsa.generate_keys(lower, upper)


@pytest.mark.parametrize("lower,upper", [(2, 4), (3, 6), (11, 14)])
def test_key_generation_uses_distinct_primes_and_round_trips(lower, upper):
    primes = [
        n
        for n in range(lower, upper)
        if n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))
    ]
    for _ in range(10):
        n, e, d = rsa.generate_keys(lower, upper)
        assert n == primes[0] * primes[1]
        phi = (primes[0] - 1) * (primes[1] - 1)
        assert e * d % phi == 1
        assert all(pow(pow(m, e, n), d, n) == m for m in range(n))


@pytest.mark.parametrize("message,padding", [(0, 3), (42, 3), (9, 1), (2454, 0)])
def test_padding_removes_suffix_and_preserves_leading_zeroes(
    monkeypatch, message, padding
):
    monkeypatch.setattr(rsa.random, "randint", lambda low, high: 0)
    assert rsa.add_padding(message, padding) == message * 10**padding
    assert rsa.remove_padding(message * 10**padding, padding) == message


@pytest.mark.parametrize("message,padding", [(-1, 0), (1, -1)])
def test_negative_padding_inputs_are_rejected(message, padding):
    with pytest.raises(ValueError):
        rsa.add_padding(message, padding)
    with pytest.raises(ValueError):
        rsa.remove_padding(message, padding)


def test_private_exponent_uses_totient_instead_of_modulus():
    assert rsa.recover_private_exponent(55, 3) == 27
    with pytest.raises(ValueError):
        rsa.recover_private_exponent(55, 4)


@pytest.mark.parametrize("padding", [0, 1])
def test_rsa_round_trip_matches_builtin_modular_power(monkeypatch, padding):
    monkeypatch.setattr(rsa.random, "randint", lambda low, high: 9)
    n, e, d = 3233, 17, 2753
    for message in (0, 1, 42, 65, 161):
        padded = message * 10**padding + (10**padding - 1)
        ciphertext = rsa.encrypt_integer(message, n, e, padding)
        assert ciphertext == pow(padded, e, n)
        assert rsa.decrypt_integer(ciphertext, n, d, padding) == message


def test_oversized_message_is_not_silently_reduced():
    with pytest.raises(ValueError):
        rsa.encrypt_integer(3233, 3233, 17, 0)
    with pytest.raises(ValueError):
        rsa.encrypt_integer(323, 3233, 17, 1)


def test_string_round_trip_includes_non_ascii_and_whitespace():
    message = " café π "
    ciphertext = rsa.encrypt_text(message, 3233, 17, 0)
    assert rsa.decrypt_text(ciphertext, 3233, 2753, 0) == message


def test_chosen_plaintext_attack_does_not_factor_or_use_a_private_key(monkeypatch):
    def unexpected_call(*args):
        pytest.fail("The chosen-plaintext lookup must use the public key only")

    monkeypatch.setattr(rsa, "recover_private_exponent", unexpected_call)
    monkeypatch.setattr(rsa.modular, "totient", unexpected_call)
    message = " café café "
    ciphertext = [pow(ord(c), 17, 3233) for c in message]
    assert rsa.recover_unpadded_text(ciphertext, 3233, 17) == message
    assert rsa.recover_unpadded_text([], 3233, 17) == ""


def test_chosen_plaintext_attack_rejects_out_of_range_ciphertext():
    with pytest.raises(ValueError):
        rsa.recover_unpadded_text([3233], 3233, 17)


def test_local_key_file_round_trip_uses_only_temporary_teaching_keys(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(register_user, "KEY_DIRECTORY", str(tmp_path / "keys"))
    monkeypatch.setattr(local_chat, "KEY_PATH", tmp_path / "keys")
    register_user.create_key_directory()
    register_user.write_public_key(3233, 17, 0, "demo_alice")
    register_user.write_private_key(2753, "demo_alice")
    assert local_chat.read_public_key("demo_alice") == (3233, 17, 0)
    assert local_chat.read_private_key("demo_alice") == 2753
    with pytest.raises(FileNotFoundError):
        local_chat.read_public_key("missing_demo_user")


def test_plaintext_input_preserves_spaces(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda prompt: " hello ")
    assert local_chat.read_plaintext() == " hello "


def test_registration_rejects_directory_separators(monkeypatch):
    replies = iter(["../other", "nested\\other", "demo_alice"])
    monkeypatch.setattr(builtins, "input", lambda prompt: next(replies))
    assert register_user.prompt_alias() == "demo_alice"


def test_local_cli_from_another_working_directory(tmp_path):
    import shutil
    import subprocess
    import sys
    from pathlib import Path

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = Path(__file__).resolve().parents[1]
    for name in ("rsa.py", "modular.py", "register_user.py", "local_chat.py"):
        shutil.copyfile(source / name, scripts / name)
    for alias in ("demo_alice", "demo_bob"):
        result = subprocess.run(
            [sys.executable, str(scripts / "register_user.py")],
            input=f"{alias}\n100\n200\n1\n",
            text=True,
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        assert "Local teaching keys saved" in result.stdout
        assert (scripts / "keys" / f"priv_{alias}.txt").is_file()
    assert not (tmp_path / "keys").exists()
    sent = subprocess.run(
        [sys.executable, str(scripts / "local_chat.py"), "demo_alice", "demo_bob"],
        input="E\n hello \nQ\n",
        text=True,
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    ciphertext = sent.stdout.split("Plaintext to encrypt: ", 1)[1].splitlines()[0]
    assert all(value.isdigit() for value in ciphertext.split())
    received = subprocess.run(
        [sys.executable, str(scripts / "local_chat.py"), "demo_bob", "demo_alice"],
        input=f"D\n{ciphertext}\nQ\n",
        text=True,
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    assert " hello " in received.stdout

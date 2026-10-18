"""Boundary cases checked against direct arithmetic, enumeration and Python's integers."""

import math
import random
import subprocess
import sys
from io import StringIO
from itertools import product
from pathlib import Path

import calculator
import modular
import pytest


def test_primes_factorisation_and_totient_against_enumeration():
    for n in range(-150, 151):
        prime = n >= 2 and all(n % d for d in range(2, n))
        assert modular.is_prime(n) == prime
        factors = modular.factorise(n)
        if n in (-1, 0, 1):
            assert factors == {}
        else:
            assert math.prod(p**power for p, power in factors.items()) == abs(n)
            assert all(p >= 2 and all(p % d for d in range(2, p)) for p in factors)
        if n > 0:
            assert modular.totient(n) == sum(
                math.gcd(k, n) == 1 for k in range(1, n + 1)
            )
    for a, b in [(-10, 2), (-5, 20), (0, 0), (5, 3), (2, 3), (10, 40)]:
        expected = [
            n for n in range(a, b) if n >= 2 and all(n % d for d in range(2, n))
        ]
        assert modular.list_primes(a, b) == expected


def test_bezout_signs_and_zero():
    for a, b in product(range(-10, 11), repeat=2):
        d, x, y = modular.bezout(a, b)
        assert d == math.gcd(a, b) == modular.gcd(a, b)
        assert a * x + b * y == d


@pytest.mark.parametrize(
    "values", [[-7], [0], [7], [-4, -10, 14], [0, 0, 0], [0, -6, 9]]
)
def test_bezout_lists(values):
    d, coefficients = modular.bezout_many(values)
    assert d == math.gcd(*values) == modular.gcd_many(values)
    assert len(coefficients) == len(values)
    assert sum(a * x for a, x in zip(values, coefficients)) == d


def test_empty_gcd_lists_raise_clear_error():
    for function in (modular.gcd_many, modular.bezout_many):
        with pytest.raises(modular.IncompatibleEquationError):
            function([])


def test_modular_powers_and_inverses_against_python():
    for n, exponent, modulus in product(range(-10, 11), range(-3, 5), range(-12, 13)):
        if modulus == 0 or (n == 0 and exponent == 0):
            with pytest.raises(ZeroDivisionError):
                modular.modular_power(n, exponent, modulus)
        elif exponent < 0 and math.gcd(n, modulus) != 1:
            with pytest.raises(ZeroDivisionError):
                modular.modular_power(n, exponent, modulus)
        else:
            assert modular.modular_power(n, exponent, modulus) == pow(
                n, exponent, abs(modulus)
            )
    for n, modulus in product(range(-10, 11), range(-12, 13)):
        if modulus == 0 or math.gcd(n, modulus) != 1:
            with pytest.raises(ZeroDivisionError):
                modular.modular_inverse(n, modulus)
        else:
            assert modular.modular_inverse(n, modulus) == pow(n, -1, abs(modulus))


@pytest.mark.parametrize("p", [2, 3, 5, 7, 11, 13])
def test_square_roots_and_residue_symbols_against_enumeration(p):
    for n in range(-p, 2 * p):
        roots = [x for x in range(p) if (x * x - n) % p == 0]
        symbol = 0 if n % p == 0 else (1 if roots else -1)
        assert modular.legendre(n, p) == symbol
        if roots:
            assert modular.modular_sqrt(n, p) in roots
        else:
            with pytest.raises(modular.IncompatibleEquationError):
                modular.modular_sqrt(n, p)


@pytest.mark.parametrize("p", [2, 3, 5, 7])
def test_quadratics_against_enumeration(p):
    for a, b, c in product(range(-1, p + 1), repeat=3):
        roots = [x for x in range(p) if (a * x * x + b * x + c) % p == 0]
        if not roots or len(roots) > 2:
            with pytest.raises(modular.IncompatibleEquationError):
                modular.solve_quadratic(a, b, c, p)
        else:
            result = modular.solve_quadratic(a, b, c, p)
            assert len(result) == 2
            assert set(result) == set(roots)


def test_invalid_prime_moduli_fail_without_entering_tonelli_shanks():
    for p in [-3, 0, 1, 4, 9, 15]:
        with pytest.raises(modular.IncompatibleEquationError):
            modular.modular_sqrt(1, p)
        with pytest.raises(modular.IncompatibleEquationError):
            modular.solve_quadratic(1, 0, -1, p)
        exception = ZeroDivisionError if p == 0 else modular.IncompatibleEquationError
        with pytest.raises(exception):
            modular.legendre(1, p)


def test_congruence_systems_against_enumeration():
    rng = random.Random(702)
    for _ in range(400):
        coefficients = [rng.randrange(-4, 5) for _ in range(3)]
        constants = [rng.randrange(-5, 6) for _ in range(3)]
        moduli = [rng.choice([-6, -4, -3, -2, -1, 1, 2, 3, 4, 6]) for _ in range(3)]
        period = math.lcm(*moduli)
        expected = [
            x
            for x in range(period)
            if all(
                (a * x - b) % p == 0 for a, b, p in zip(coefficients, constants, moduli)
            )
        ]
        if not expected:
            with pytest.raises(modular.IncompatibleEquationError):
                modular.solve_congruences(coefficients, constants, moduli)
        else:
            residue, modulus = modular.solve_congruences(
                coefficients, constants, moduli
            )
            assert 0 <= residue < modulus
            assert [x for x in range(period) if x % modulus == residue] == expected
    assert modular.solve_congruences([], [], []) == (0, 1)
    for args in [([0], [0], [0]), ([1], [1], [0]), ([1], [], [2])]:
        with pytest.raises(modular.IncompatibleEquationError):
            modular.solve_congruences(*args)


@pytest.mark.parametrize(
    "command,expected",
    [
        ("solve_extra([1;1;3])", "INVALID"),
        ("solve([1;1;3]) trailing text", "INVALID"),
        ("solve(1;1;3)", "INVALID"),
        ("solve([1;1;3],)", "INVALID"),
        ("solve([1;1;3] , [4;7;11])", "10 (mod 33)"),
        ("prime(7,)", "INVALID"),
        ("sqrt(9,3)", "0"),
        ("sqrt(1,2)", "1"),
        ("quadratic(5,1,1,5)", "4"),
        ("quadratic(1,1,0,2)", "0, 1"),
        ("quadratic(0,0,0,5)", "INVALID"),
        ("pow(2,0,1)", "0"),
        ("inv(2,-7)", "4"),
    ],
)
def test_command_regressions(command, expected):
    assert calculator.try_command(command) == expected


def test_batch_stops_at_blank_line():
    output = StringIO()
    calculator.run_commands(StringIO("prime(7)\n\nprimo(11)\n"), output)
    assert output.getvalue() == "Yes\n"


def test_batch_cli_preserves_input_when_paths_are_identical(tmp_path):
    commands = tmp_path / "commands.txt"
    original = "prime(7)\n"
    commands.write_text(original, encoding="utf-8")
    script = Path(calculator.__file__)
    result = subprocess.run(
        [sys.executable, str(script), str(commands), str(commands)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert commands.read_text(encoding="utf-8") == original


def test_supplied_example_output():
    examples = Path(__file__).resolve().parents[1] / "examples"
    output = StringIO()
    with (examples / "commands.txt").open(encoding="utf-8") as commands:
        calculator.run_commands(commands, output)
    assert (
        output.getvalue().splitlines()
        == (examples / "expected-output.txt").read_text(encoding="utf-8").splitlines()
    )


def test_batch_cli_preserves_input_when_output_is_a_hard_link(tmp_path):
    commands = tmp_path / "commands.txt"
    output = tmp_path / "output.txt"
    original = "prime(7)\n"
    commands.write_text(original, encoding="utf-8")
    output.hardlink_to(commands)
    result = subprocess.run(
        [sys.executable, str(Path(calculator.__file__)), str(commands), str(output)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert commands.read_text(encoding="utf-8") == original
    assert "different files" in result.stderr

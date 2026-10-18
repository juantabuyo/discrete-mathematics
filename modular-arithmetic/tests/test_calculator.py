from io import StringIO

import calculator
import pytest


def try_command(command: str, expected_output: str) -> None:
    input = StringIO(command + "\n")
    output = StringIO()
    calculator.run_commands(input, output)
    assert output.getvalue() == expected_output + "\n"


@pytest.mark.parametrize(
    "command,expected_output",
    [
        ("prime(7)", "Yes"),
        ("prime(12)", "No"),
        ("prime(-2)", "No"),
        (
            "primes(5,100)",
            "5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97",
        ),
        ("factorise(8)", "2: 3"),
        ("gcd(1,20)", "1"),
        ("coprime(5,3)", "Yes"),
        ("coprime(6,9)", "No"),
        ("pow(2,5,3)", "2"),
        ("pow(-3,-8,7)", "4"),
        ("pow(100,100,3)", "1"),
        ("inv(3,7)", "5"),
        ("inv(3,9)", "NO_SOLUTION"),
        ("totient(10)", "4"),
        ("legendre(10,3)", "1"),
        ("Legendre(10,3)", "INVALID"),
        ("solve([1;1;3],[4;7;11])", "10 (mod 33)"),
        ("sqrt(-1,5)", "2, 3"),
        ("quadratic(4,1,3,11)", "NO_SOLUTION"),
        ("quadratic(4,1,5,11)", "3, 5"),
        ("quadratic(1,2,1,11)", "10"),
    ],
)
def test_calculator_basic(command: str, expected_output: str) -> None:
    try_command(command, expected_output)

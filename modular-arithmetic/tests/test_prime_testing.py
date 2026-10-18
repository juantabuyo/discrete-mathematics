import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "n,expected_output",
    [
        (2, True),
        (3, True),
        (4, False),
        (5, True),
    ],
)
def test_is_prime_basic(n: int, expected_output: bool) -> None:
    assert modular.is_prime(n) == expected_output


@pytest.mark.parametrize(
    "n,expected_output",
    [
        (4, "No"),
        (5, "Yes"),
    ],
)
def test_is_prime_calculator(n: int, expected_output: str) -> None:
    try_command(f"prime({n})", expected_output)

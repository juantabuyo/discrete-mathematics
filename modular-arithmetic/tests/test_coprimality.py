import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "a,b,expected_output",
    [
        (14, 20, False),
        (14, 15, True),
    ],
)
def test_coprime_basic(a: int, b: int, expected_output: bool) -> None:
    assert modular.coprime(a, b) == expected_output


@pytest.mark.parametrize(
    "a,b,expected_output",
    [
        (14, 20, "No"),
        (14, 15, "Yes"),
    ],
)
def test_coprime_calculator(a: int, b: int, expected_output: str) -> None:
    try_command(f"coprime({a},{b})", expected_output)

import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize("n,expected_output", [(7, 6), (15, 8)])
def test_totient_basic(n: int, expected_output: int) -> None:
    assert modular.totient(n) == expected_output


@pytest.mark.parametrize("n,expected_output", [(7, "6"), (15, "8")])
def test_totient_calculator(n: int, expected_output: str) -> None:
    try_command(f"totient({n})", expected_output)

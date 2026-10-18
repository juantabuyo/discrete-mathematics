import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "n,p,expected_output",
    [
        (2, 7, 4),
    ],
)
def test_modular_inverse_basic(n: int, p: int, expected_output: int) -> None:
    assert modular.modular_inverse(n, p) == expected_output


def test_modular_inverse_zero():
    """Invalid problems raise the documented exception."""
    with pytest.raises(ZeroDivisionError):
        modular.modular_inverse(2, 0)


@pytest.mark.parametrize("n,p,expected_output", [(2, 7, "4"), (2, 0, "NO_SOLUTION")])
def test_inverse_calculator(n: int, p: int, expected_output: str) -> None:
    try_command(f"inv({n},{p})", expected_output)

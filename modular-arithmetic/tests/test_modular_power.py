import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "base,exp,p,expected_output",
    [
        (2, 3, 7, 1),
    ],
)
def test_modular_power_basic(base: int, exp: int, p: int, expected_output: int) -> None:
    assert modular.modular_power(base, exp, p) == expected_output


def test_modular_power_zero():
    """Invalid problems raise the documented exception."""
    with pytest.raises(ZeroDivisionError):
        modular.modular_power(2, 3, 0)
    with pytest.raises(ZeroDivisionError):
        modular.modular_power(0, 0, 7)


@pytest.mark.parametrize(
    "base,exp,p,expected_output", [(2, 3, 7, "1"), (0, 0, 0, "NO_SOLUTION")]
)
def test_power_calculator(base: int, exp: int, p: int, expected_output: str) -> None:
    try_command(f"pow({base},{exp},{p})", expected_output)

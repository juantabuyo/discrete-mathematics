import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "n,p,expected_output",
    [
        (2, 5, -1),
        (2, 7, 1),
        (10, 5, 0),
    ],
)
def test_legendre_basic(n: int, p: int, expected_output: int) -> None:
    assert modular.legendre(n, p) == expected_output


def test_legendre_zero():
    """Invalid problems raise the documented exception."""
    with pytest.raises(ZeroDivisionError):
        modular.legendre(2, 0)


@pytest.mark.parametrize(
    "n,p,expected_output",
    [
        (2, 5, "-1"),
        (2, 7, "1"),
        (10, 5, "0"),
        (2, 0, "NO_SOLUTION"),
    ],
)
def test_legendre_calculator(n: int, p: int, expected_output: str) -> None:
    try_command(f"legendre({n},{p})", expected_output)

import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "n,p,expected_root1,expected_root2",
    [
        (2, 7, 3, 4),
    ],
)
def test_modular_sqrt_basic(
    n: int, p: int, expected_root1: int, expected_root2: int
) -> None:
    assert (
        modular.modular_sqrt(n, p) % p == expected_root1
        or modular.modular_sqrt(n, p) % p == expected_root2
    )


def test_modular_sqrt_no_solution():
    """Invalid problems raise the documented exception."""
    with pytest.raises(modular.IncompatibleEquationError):
        modular.modular_sqrt(2, 5)


@pytest.mark.parametrize(
    "n,p,expected_output",
    [
        (2, 5, "NO_SOLUTION"),
        (2, 7, "3, 4"),
        (9, 3, "0"),
    ],
)
def test_square_roots_calculator(n: int, p: int, expected_output: str) -> None:
    try_command(f"sqrt({n},{p})", expected_output)


@pytest.mark.parametrize(
    "a,b,c,p,expected_root1,expected_root2",
    [
        (4, 1, 5, 11, 3, 5),
        (1, 2, 1, 11, 10, 10),
    ],
)
def test_solve_quadratic_basic(
    a: int, b: int, c: int, p: int, expected_root1: int, expected_root2: int
) -> None:
    assert modular.solve_quadratic(a, b, c, p) == (
        expected_root1,
        expected_root2,
    ) or modular.solve_quadratic(a, b, c, p) == (expected_root2, expected_root1)


@pytest.mark.parametrize(
    "a,b,c,p",
    [
        (4, 1, 3, 11),
    ],
)
def test_solve_quadratic_no_solution(a: int, b: int, c: int, p: int) -> None:
    """Invalid problems raise the documented exception."""
    with pytest.raises(modular.IncompatibleEquationError):
        modular.solve_quadratic(a, b, c, p)


@pytest.mark.parametrize(
    "a,b,c,p,expected_output",
    [
        (4, 1, 5, 11, "3, 5"),
        (1, 2, 1, 11, "10"),
        (4, 1, 3, 11, "NO_SOLUTION"),
    ],
)
def test_quadratic_equation_calculator(
    a: int, b: int, c: int, p: int, expected_output: str
) -> None:
    try_command(f"quadratic({a},{b},{c},{p})", expected_output)

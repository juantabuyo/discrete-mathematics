from typing import List, Tuple

import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "alist,blist,plist,expected_output",
    [
        ([2], [3], [5], (4, 5)),
        ([2], [4], [6], (2, 3)),
        ([1, 4], [1, 7], [3, 11], (10, 33)),
    ],
)
def test_congruence_basic(
    alist: List[int],
    blist: List[int],
    plist: List[int],
    expected_output: Tuple[int, int],
) -> None:
    assert modular.solve_congruences(alist, blist, plist) == expected_output


@pytest.mark.parametrize(
    "alist,blist,plist,expected_output",
    [
        ([2], [4], [6], (2, 3)),
        ([1, 4], [1, 7], [3, 11], (10, 33)),
    ],
)
def test_congruence_non_coprime(
    alist: List[int],
    blist: List[int],
    plist: List[int],
    expected_output: Tuple[int, int],
) -> None:
    assert modular.solve_congruences(alist, blist, plist) == expected_output


@pytest.mark.parametrize(
    "alist,blist,plist",
    [
        ([2], [3], [4]),
        ([1, 1], [1, 2], [5, 5]),
    ],
)
def test_inconsistent_system(alist: List[int], blist: List[int], plist: List[int]):
    """Invalid problems raise the documented exception."""
    with pytest.raises(modular.IncompatibleEquationError):
        modular.solve_congruences(alist, blist, plist)


@pytest.mark.parametrize(
    "command,expected_output",
    [("solve([2;4;6])", "2 (mod 3)"), ("solve([1;1;3],[4;7;11])", "10 (mod 33)")],
)
def test_solve_calculator(command: str, expected_output: str) -> None:
    try_command(command, expected_output)

from typing import List

import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "a,b,expected_output",
    [
        (1, 11, [2, 3, 5, 7]),
        (8, 10, []),
    ],
)
def test_list_primes_basic(a: int, b: int, expected_output: List[int]) -> None:
    assert modular.list_primes(a, b) == expected_output


@pytest.mark.parametrize(
    "a,b,expected_output",
    [
        (1, 11, "2, 3, 5, 7"),
        (8, 10, "NO_SOLUTION"),
    ],
)
def test_list_primes_calculator(a: int, b: int, expected_output: str) -> None:
    try_command(f"primes({a},{b})", expected_output)

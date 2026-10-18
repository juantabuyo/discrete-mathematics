from typing import List

import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "a,b,expected_output",
    [
        (10, 15, 5),
    ],
)
def test_gcd_basic(a: int, b: int, expected_output: int) -> None:
    assert modular.gcd(a, b) == expected_output


@pytest.mark.parametrize(
    "a,b,expected_gcd",
    [
        (6, 10, 2),
    ],
)
def test_bezout_basic(a: int, b: int, expected_gcd: int) -> None:
    (d, x, y) = modular.bezout(a, b)
    assert d == expected_gcd
    assert a * x + b * y == d


@pytest.mark.parametrize(
    "nlist,expected_output",
    [
        ([4, 10, 14], 2),
    ],
)
def test_gcd_many_basic(nlist: List[int], expected_output: int) -> None:
    assert modular.gcd_many(nlist) == expected_output


@pytest.mark.parametrize(
    "nlist,expected_gcd",
    [
        ([4, 10, 14], 2),
    ],
)
def test_bezout_many_basic(nlist: List[int], expected_gcd: int) -> None:
    (d, X) = modular.bezout_many(nlist)
    assert d == expected_gcd
    assert len(X) == len(nlist)
    total = 0
    for i in range(len(X)):
        total += X[i] * nlist[i]
    assert total == d


@pytest.mark.parametrize(
    "command,expected_output",
    [
        ("gcd(10,15)", "5"),
        ("gcd(4)", "4"),
        ("gcd(4,10,14)", "2"),
    ],
)
def test_gcd_many_calculator(command: str, expected_output: str) -> None:
    try_command(command, expected_output)

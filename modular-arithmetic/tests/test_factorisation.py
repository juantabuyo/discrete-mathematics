from typing import Dict

import modular
import pytest
from test_calculator import try_command


@pytest.mark.parametrize(
    "n,expected_output", [(2, {2: 1}), (12, {2: 2, 3: 1}), (0, {})]
)
def test_factorise_basic(n: int, expected_output: Dict[int, int]) -> None:
    assert modular.factorise(n) == expected_output


@pytest.mark.parametrize(
    "n,expected_output",
    [
        (2, "2: 1"),
        (12, "2: 2, 3: 1"),
        (0, "0"),
    ],
)
def test_factorise_calculator(n: int, expected_output: str) -> None:
    try_command(f"factorise({n})", expected_output)

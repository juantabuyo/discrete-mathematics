import pytest
import rsa


@pytest.mark.parametrize(
    "m,padding_digits,expected_output",
    [
        (2454, 1, 245),
        (2454, 2, 24),
        (2454, 3, 2),
        (2432, 2, 24),
        (2432, 0, 2432),
    ],
)
def test_remove_padding(m: int, padding_digits: int, expected_output: int) -> None:
    assert rsa.remove_padding(m, padding_digits) == expected_output


@pytest.mark.parametrize(
    "m,padding_digits",
    [(m, padding_digits) for m in range(10) for padding_digits in range(3)],
)
def test_add_padding(m: int, padding_digits: int) -> None:
    assert rsa.remove_padding(rsa.add_padding(m, padding_digits), padding_digits) == m

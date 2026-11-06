import modular
import pytest
import rsa


@pytest.mark.parametrize("rnd", range(10))
def test_generate_keys(rnd: int) -> None:
    (n, e, d) = rsa.generate_keys(1000, 10000)
    assert e * d % modular.totient(n) == 1


@pytest.mark.parametrize(
    "n,e,d",
    [
        (809570247883, 77204266853, 42840500717),
    ],
)
def test_recover_private_exponent(n: int, e: int, d: int) -> None:
    assert rsa.recover_private_exponent(n, e) == d


@pytest.mark.parametrize("rnd", range(10))
def test_generate_and_recover_keys(rnd: int) -> None:
    (n, e, d) = rsa.generate_keys(1000, 10000)
    assert rsa.recover_private_exponent(n, e) == d

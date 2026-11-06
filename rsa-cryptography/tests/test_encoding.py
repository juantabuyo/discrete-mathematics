import rsa


def test_encode_text() -> None:
    assert rsa.encode_text("Hello, π!") == [72, 101, 108, 108, 111, 44, 32, 960, 33]


def test_decode_text() -> None:
    assert rsa.decode_text([72, 101, 108, 108, 111, 44, 32, 960, 33]) == "Hello, π!"

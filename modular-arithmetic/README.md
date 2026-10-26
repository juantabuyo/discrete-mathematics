# Modular arithmetic

A number-theory library and command-line calculator in Python. It covers prime testing, a sieve, factorisation, Euclidean algorithms, modular powers and inverses, Euler's totient, congruences and square roots.

`modular.py` contains the algorithms. `calculator.py` runs commands interactively or from a file. The congruence solver allows non-coprime moduli; square roots use Tonelli–Shanks for odd primes.

## Run

Use Python 3.12. The application uses only the standard library. Run from this folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python calculator.py
```

On Windows, activate with `.venv\Scripts\activate`. Example commands:

```text
factorise(120)
solve([1;1;3],[4;7;11])
sqrt(-1,5)
```

They return `2: 3, 3: 1, 5: 1`, `10 (mod 33)` and `2, 3`. Press Enter on an empty line to exit; startup help lists the commands.

For a repeatable batch example:

```bash
python calculator.py examples/commands.txt output.txt
```

Compare with [expected-output.txt](examples/expected-output.txt). The output file is replaced. Input and output must be different files, including when accessed through links. Processing stops at a blank line or end of file.

The library can also be imported:

```python
from modular import bezout, modular_inverse

print(bezout(6, 10))        # (2, 2, -1)
print(modular_inverse(2, 7))  # 4
```

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```

Tests compare results with enumeration and Python's integer arithmetic, including negative powers, signed Bézout identities and non-coprime congruences. They also check parsing and batch-file handling.

## Conventions and limits

- Commands are case-sensitive. `Yes`/`No` are Boolean answers; `NO_SOLUTION` means no result exists and `INVALID` means invalid or unsupported input.
- Powers and inverses use the absolute value of a non-zero modulus. The exercise rejects `0**0`.
- Root and quadratic routines require prime moduli. The quadratic interface returns at most two roots, so it rejects an equation solved by every residue when the modulus exceeds two.
- Trial division and the sieve are intended for small inputs, not cryptographic-size integers.

## Academic context and credits

This was a two-person Discrete Mathematics coursework project at ICAI. Course interfaces and test cases provided the starting point. Post-submission changes corrected boundary cases and parsing, protected batch input from accidental overwriting, and translated the interface to English.

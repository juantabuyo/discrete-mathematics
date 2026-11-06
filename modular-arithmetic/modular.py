"""Integer and modular arithmetic for the IMAT-LAB command interface."""

import math
from typing import Dict, List, Tuple


class IncompatibleEquationError(Exception):
    pass


def is_prime(n: int) -> bool:
    """Return whether n is prime, using trial division by candidates of the form 6k ± 1."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    if n % 3 == 0:
        return n == 3
    limit = math.isqrt(n)
    i = 5
    while i <= limit:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def list_primes(a, b) -> List[int]:
    """Return the primes in the half-open interval [a, b), using a sieve."""

    if b <= 2 or a >= b:
        return []
    sieve = [True] * b
    sieve[0] = False
    if b > 1:
        sieve[1] = False
    for i in range(2, math.isqrt(b) + 1):
        if sieve[i]:
            for j in range(i * i, b, i):
                sieve[j] = False
    return [i for i in range(max(a, 2), b) if sieve[i]]


def factorise(n: int) -> Dict[int, int]:
    """Return the prime factors of abs(n) and their exponents. Return {} for -1, 0 and 1."""
    if n in (-1, 0, 1):
        return {}
    n = abs(n)
    f = {}
    while n % 2 == 0:
        f[2] = f.get(2, 0) + 1
        n //= 2
    while n % 3 == 0:
        f[3] = f.get(3, 0) + 1
        n //= 3
    p = 5
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        q = p + 2
        while q * q <= n and n % q == 0:
            f[q] = f.get(q, 0) + 1
            n //= q
        p += 6
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def gcd(a: int, b: int) -> int:
    """Return the non-negative greatest common divisor of a and b."""
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def bezout(n: int, m: int) -> Tuple[int, int, int]:
    """Return (d, x, y), where d is non-negative and n*x + m*y == d."""
    a, b = n, m
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while b != 0:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    if a < 0:
        a, x0, y0 = -a, -x0, -y0
    return (a, x0, y0)


def gcd_many(nlist: List[int]) -> int:
    """Return the non-negative greatest common divisor of a non-empty integer list."""
    from functools import reduce

    if not nlist:
        raise IncompatibleEquationError("At least one integer is required")
    return reduce(gcd, nlist, 0)


def bezout_many(nlist: List[int]) -> Tuple[int, List[int]]:
    """Return (d, coefficients) satisfying the Bézout identity for a non-empty list."""
    if not nlist:
        raise IncompatibleEquationError("At least one integer is required")

    def combine_bezout(values):
        if len(values) == 1:
            return abs(values[0]), [-1 if values[0] < 0 else 1]
        if len(values) == 2:
            d, x, y = bezout(values[0], values[1])
            return d, [x, y]
        else:
            d1, coef1 = combine_bezout(values[:-1])
            d2, x2, y2 = bezout(d1, values[-1])
            coefs = [c * x2 for c in coef1] + [y2]
            return d2, coefs

    return combine_bezout(nlist)


def coprime(n: int, m: int) -> bool:
    """Return whether n and m have greatest common divisor 1."""
    return gcd(n, m) == 1


def modular_power(base: int, exp: int, p: int) -> int:
    """Return base**exp modulo abs(p) by repeated squaring.

    Negative exponents require an invertible base. A zero modulus or 0**0
    raises ZeroDivisionError, following the coursework convention.
    """
    if p == 0:
        raise ZeroDivisionError("The modulus must not be zero")
    if base == 0 and exp == 0:
        raise ZeroDivisionError("0**0 is undefined")
    p = abs(p)
    if exp < 0:
        base = modular_inverse(base, p)
        exp = -exp
    res = 1 % p
    base = base % p
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % p
        base = (base * base) % p
        exp //= 2
    return res


def modular_inverse(n: int, p: int) -> int:
    """Return the inverse of n modulo abs(p).

    Raise ZeroDivisionError for a zero modulus or a non-invertible n.
    """
    if p == 0:
        raise ZeroDivisionError("The modulus must not be zero")
    p = abs(p)
    d, x, y = bezout(n, p)
    if d != 1:
        raise ZeroDivisionError(f"{n} has no inverse modulo {p}")
    return x % p


def totient(n: int) -> int:
    """Return Euler's totient for positive n, or 0 for non-positive n."""
    if n <= 0:
        return 0
    factors = factorise(n)
    res = n
    for p in factors:
        res = res // p * (p - 1)
    return res


def legendre(n: int, p: int) -> int:
    """Return the quadratic-residue symbol for n modulo a prime p.

    Return 0 for multiples of p, 1 for non-zero squares and -1 otherwise.
    The coursework extends this definition to p == 2.
    """
    if p == 0:
        raise ZeroDivisionError("The modulus must not be zero")
    if not is_prime(p):
        raise IncompatibleEquationError("The modulus must be prime")
    n = n % p
    if n == 0:
        return 0
    r = modular_power(n, (p - 1) // 2, p)
    if r == 1:
        return 1
    elif r == p - 1:
        return -1
    else:
        return 0


def solve_congruences(
    alist: List[int], blist: List[int], plist: List[int]
) -> Tuple[int, int]:
    """Solve a_i*x == b_i (mod p_i), including non-coprime moduli.

    Return (r, m) with 0 <= r < m. Negative moduli are normalised to
    positive values. Empty lists give (0, 1), representing all integers.
    Raise IncompatibleEquationError for inconsistent or invalid systems.
    """
    if len(alist) != len(blist) or len(alist) != len(plist):
        raise IncompatibleEquationError("The lists must have equal lengths")
    n = len(alist)
    x, m = 0, 1
    for i in range(n):
        a, b, p = alist[i], blist[i], abs(plist[i])
        if p == 0:
            raise IncompatibleEquationError("The modulus must not be zero")
        d = gcd(a, p)
        if b % d != 0:
            raise IncompatibleEquationError("The congruences are inconsistent")
        a1, b1, p1 = a // d, b // d, p // d
        if p1 == 1:
            continue
        try:
            inv_a1 = modular_inverse(a1 % p1, p1)
        except ZeroDivisionError:
            raise IncompatibleEquationError("The congruences are inconsistent")
        r_i = (inv_a1 * (b1 % p1)) % p1
        # Merge this residue with the accumulated solution, allowing shared factors.
        g, s, _ = bezout(m, p1)
        if (r_i - x) % g != 0:
            raise IncompatibleEquationError("The congruences are inconsistent")
        k = ((r_i - x) // g * s) % (p1 // g)
        x = x + m * k
        m = m * (p1 // g)
        x %= m
    return x % m, m


def modular_sqrt(n: int, p: int) -> int:
    """Return one square root of n modulo the prime p.

    Use Tonelli–Shanks for odd primes. Raise IncompatibleEquationError
    when no root exists or the modulus is not prime.
    """

    if not is_prime(p):
        raise IncompatibleEquationError("The modulus must be prime")
    if p == 2:
        return n % 2
    n %= p
    if n == 0:
        return 0
    if legendre(n, p) != 1:
        raise IncompatibleEquationError("No modular square root exists")
    # Factor p - 1 into an odd q and a power of two for Tonelli–Shanks.
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre(z, p) != -1:
        z += 1
    c = modular_power(z, q, p)
    x = modular_power(n, (q + 1) // 2, p)
    t = modular_power(n, q, p)
    m = s
    while t != 1:
        i = 1
        temp = (t * t) % p
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
        b = modular_power(c, 2 ** (m - i - 1), p)
        x = (x * b) % p
        t = (t * b * b) % p
        c = (b * b) % p
        m = i
    return x


def solve_quadratic(a: int, b: int, c: int, p: int) -> Tuple[int, int]:
    """Return the roots of a*x**2 + b*x + c modulo a prime p.

    Repeat a single root in the returned pair. A linear equation is
    supported when a is zero modulo p. Raise IncompatibleEquationError
    when there are no roots, or all residues are roots for p > 2
    (which cannot be represented by this two-root interface).
    """
    if not is_prime(p):
        raise IncompatibleEquationError("The modulus must be prime")
    a, b, c = a % p, b % p, c % p
    if p == 2:
        roots = [x for x in (0, 1) if (a * x * x + b * x + c) % p == 0]
        if not roots:
            raise IncompatibleEquationError("The equation has no solution")
        return roots[0], roots[-1]
    if a == 0:
        if b == 0:
            if c == 0:
                raise IncompatibleEquationError(
                    "All residues solve the equation; two roots cannot represent them"
                )
            raise IncompatibleEquationError("The equation has no solution")
        x = (-c * modular_inverse(b, p)) % p
        return (x, x)
    D = (b * b - 4 * a * c) % p
    if legendre(D, p) == -1:
        raise IncompatibleEquationError("The equation has no roots modulo p")
    sqrt_D = modular_sqrt(D, p)
    inv_2a = modular_inverse(2 * a, p)
    x1 = ((-b + sqrt_D) * inv_2a) % p
    x2 = ((-b - sqrt_D) * inv_2a) % p
    return (x1, x2)

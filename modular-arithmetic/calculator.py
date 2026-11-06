"""Interactive and batch access to the modular arithmetic library."""

import io
import re
import sys
from pathlib import Path
from typing import Dict, List, TextIO, Tuple

import modular
from modular import IncompatibleEquationError

YES = "Yes"
NO = "No"


def format_boolean(b: bool) -> str:
    return YES if b else NO


def is_integer(num_str: str) -> bool:
    try:
        int(num_str)
        return True
    except Exception:
        return False


def split_arguments(args: str) -> List[str]:
    parts = []
    buffer = []
    depth = 0
    for character in args:
        if character == "," and depth == 0:
            parts.append("".join(buffer).strip())
            buffer = []
        else:
            if character == "[":
                depth += 1
            elif character == "]":
                depth = max(0, depth - 1)
            buffer.append(character)
    if buffer or args.endswith(","):
        parts.append("".join(buffer).strip())
    return parts


def parse_congruences(args: str) -> None | Tuple[List[int], List[int], List[int]]:
    A = []
    B = []
    P = []
    for elements in split_arguments(args):
        s = elements.strip()
        if not (s.startswith("[") and s.endswith("]")):
            return None
        s = s[1:-1].strip()
        parts = [x.strip() for x in s.split(";")]
        if len(parts) != 3:
            return None
        try:
            a = int(parts[0])
            b = int(parts[1])
            p = int(parts[2])
        except ValueError:
            return None
        A.append(a)
        B.append(b)
        P.append(p)
    if not A:
        return None
    return A, B, P


def format_factorisation(factors: Dict[int, int]) -> str:
    parts = []
    for num, exp in sorted(factors.items()):
        parts.append(f"{num}: {exp}")
    return ", ".join(parts)


def command_prime(args: List[str], interactive: bool) -> str:
    if len(args) != 1 or not is_integer(args[0]):
        return "INVALID" if not interactive else "Error: prime(n), expected one integer"
    n = int(args[0])
    return format_boolean(modular.is_prime(n))


def command_primes(args: List[str], interactive: bool) -> str:
    if len(args) != 2 or not all(is_integer(x) for x in args):
        return (
            "INVALID"
            if not interactive
            else "Error: primes(a,b), expected two integers"
        )
    a, b = int(args[0]), int(args[1])
    if a >= b:
        return "INVALID" if not interactive else "Error: a must be less than b"
    values = modular.list_primes(a, b)
    if not values:
        return "NO_SOLUTION"
    return ", ".join(str(n) for n in values)


def command_factorise(args: List[str], interactive: bool) -> str:
    if len(args) != 1 or not is_integer(args[0]):
        return (
            "INVALID"
            if not interactive
            else "Error: factorise(n), expected one integer"
        )
    n = int(args[0])
    try:
        if n in (-1, 0, 1):
            return str(n)
        fac = modular.factorise(n)
        return format_factorisation(fac)
    except Exception:
        return "INVALID" if not interactive else "Error: factorisation failed"


def command_gcd(args: List[str], interactive: bool) -> str:
    if len(args) < 1 or not all(is_integer(x) for x in args):
        return (
            "INVALID"
            if not interactive
            else "Error: gcd(a,b,...), expected one or more integers"
        )
    vals = [int(x) for x in args]
    try:
        if len(vals) == 1:
            return str(abs(vals[0]))
        if len(vals) == 2:
            return str(modular.gcd(vals[0], vals[1]))
        return str(modular.gcd_many(vals))
    except Exception:
        return "INVALID" if not interactive else "Error: failed gcd"


def command_coprime(args: List[str], interactive: bool) -> str:
    if len(args) != 2 or not all(is_integer(x) for x in args):
        return (
            "INVALID"
            if not interactive
            else "Error: coprime(a,b), expected two integers"
        )
    a, b = int(args[0]), int(args[1])
    try:
        return format_boolean(modular.coprime(a, b))
    except Exception:
        return "INVALID" if not interactive else "Error: failed coprime"


def pow_pos(base: int, exp: int, p: int) -> int:
    return modular.modular_power(base, exp, p)


def command_power(args: List[str], interactive: bool) -> str:
    if len(args) != 3 or not all(is_integer(x) for x in args):
        return (
            "INVALID"
            if not interactive
            else "Error: pow(base,exp,p), expected three integers"
        )
    base, exp, p = int(args[0]), int(args[1]), int(args[2])
    try:
        if exp < 0:
            try:
                inv = modular.modular_inverse(base, p)
            except ZeroDivisionError as e:
                return "NO_SOLUTION" if not interactive else str(e)
            except Exception:
                return "INVALID" if not interactive else "Error: failed inv(n,p)"
            return str(pow_pos(inv, -exp, p))
        return str(pow_pos(base, exp, p))
    except ZeroDivisionError as e:
        return "NO_SOLUTION" if not interactive else str(e)
    except Exception:
        return "INVALID" if not interactive else "Error: failed pow"


def command_inverse(args: List[str], interactive: bool) -> str:
    if len(args) != 2 or not all(is_integer(x) for x in args):
        return "INVALID" if not interactive else "Error: inv(n,p),expected two integers"
    n, p = int(args[0]), int(args[1])
    try:
        return str(modular.modular_inverse(n, p))
    except ZeroDivisionError as e:
        return "NO_SOLUTION" if not interactive else str(e)


def command_totient(args: List[str], interactive: bool) -> str:
    if len(args) != 1 or not is_integer(args[0]):
        return (
            "INVALID" if not interactive else "Error: totient(n), expected one integer"
        )
    n = int(args[0])
    if n <= 0:
        return "INVALID" if not interactive else "Error: n must be positive"
    try:
        return str(modular.totient(n))
    except Exception:
        return "INVALID" if not interactive else "Error: failed totient"


def command_legendre(args: List[str], interactive: bool) -> str:
    if len(args) != 2 or not all(is_integer(x) for x in args):
        return (
            "INVALID"
            if not interactive
            else "Error: legendre(n,p), expected two integers"
        )
    n, p = int(args[0]), int(args[1])
    try:
        return str(modular.legendre(n, p))
    except ZeroDivisionError as e:
        return "NO_SOLUTION" if not interactive else str(e)
    except Exception:
        return "INVALID" if not interactive else "Error: failed legendre"


def command_sqrt(args: List[str], interactive: bool) -> str:
    if len(args) != 2 or not all(is_integer(x) for x in args):
        return (
            "INVALID" if not interactive else "Error: sqrt(n,p), expected two integers"
        )
    n, p = int(args[0]), int(args[1])
    if not modular.is_prime(p):
        return "INVALID" if not interactive else "Error: p must be prime"
    try:
        r = modular.modular_sqrt(n, p)
        if r is None:
            return "NO_SOLUTION"
        r = r % p
        r2 = (-r) % p
        if r2 == r:
            return str(r)
        a, b = sorted((r, r2))
        return f"{a}, {b}"
    except IncompatibleEquationError as e:
        return "NO_SOLUTION" if not interactive else str(e)
    except Exception:
        return "INVALID" if not interactive else "Error: failed sqrt"


def command_quadratic(args: List[str], interactive: bool) -> str:
    if len(args) != 4 or not all(is_integer(x) for x in args):
        return (
            "INVALID"
            if not interactive
            else "Error: quadratic(a,b,c,p), expected four integers"
        )
    a, b, c, p = int(args[0]), int(args[1]), int(args[2]), int(args[3])
    if not modular.is_prime(p):
        return "INVALID" if not interactive else "Error: p must be prime"
    if p > 2 and a % p == b % p == c % p == 0:
        return (
            "INVALID"
            if not interactive
            else "All residues are solutions; the two-root interface cannot represent them"
        )
    try:
        x1, x2 = modular.solve_quadratic(a, b, c, p)
        if x1 is None and x2 is None:
            return "NO_SOLUTION" if not interactive else "Error: no solution exists"
        x1 %= p
        x2 %= p
        if x1 == x2:
            return str(x1)
        xs = sorted([x1, x2])
        return f"{xs[0]}, {xs[1]}"
    except IncompatibleEquationError as e:
        return "NO_SOLUTION" if not interactive else str(e)
    except Exception:
        return "INVALID" if not interactive else "Error: failed quadratic"


def command_solve(args: str, interactive: bool) -> str:
    elements = parse_congruences(args)
    if elements is None:
        return (
            "INVALID" if not interactive else "Error: solve([a;b;p],...) invalid format"
        )
    A, B, P = elements
    if not (len(A) == len(B) == len(P)) or len(A) == 0:
        return "INVALID" if not interactive else "Error: empty or unequal lists"
    if any(p == 0 for p in P):
        return "INVALID" if not interactive else "Error: zero modulus is not allowed"
    try:
        r, m = modular.solve_congruences(A, B, P)
        return f"{r} (mod {m})"
    except IncompatibleEquationError as e:
        return "NO_SOLUTION" if not interactive else str(e)
    except Exception:
        return "INVALID" if not interactive else "Error: failed solve"


COMMANDS = {
    "prime": command_prime,
    "primes": command_primes,
    "factorise": command_factorise,
    "gcd": command_gcd,
    "coprime": command_coprime,
    "pow": command_power,
    "inv": command_inverse,
    "totient": command_totient,
    "legendre": command_legendre,
    "sqrt": command_sqrt,
    "quadratic": command_quadratic,
}

COMMAND_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$")


def process_line(line: str, interactive: bool) -> str:
    line = line.strip()
    if not line:
        return ""
    m = COMMAND_PATTERN.match(line)
    if not m:
        return "INVALID" if not interactive else "Error: invalid command or syntax"

    name, args = m.groups()
    if name == "solve":
        try:
            return command_solve(args, interactive)
        except Exception:
            return "INVALID" if not interactive else "Error: failed solve"
    command = COMMANDS.get(name)
    if command is None:
        return (
            "INVALID"
            if not interactive
            else f"Error: command '{name}' is not supported"
        )

    arguments = split_arguments(args)
    try:
        return command(arguments, interactive)
    except IncompatibleEquationError:
        return "NO_SOLUTION"
    except Exception:
        return "INVALID" if not interactive else "Error: internal error"


def run_commands(fin: TextIO, fout: TextIO) -> None:
    """Run one command per line until a blank line or end of input."""
    interactive = False
    while True:
        line = fin.readline()
        if line == "":
            break
        if line.strip() == "":
            break
        out = process_line(line, interactive)
        if out != "":
            print(out, file=fout)


def try_command(command: str) -> str:
    input_io = io.StringIO(command.strip() + "\n\n")
    output_io = io.StringIO()
    run_commands(input_io, output_io)
    lines = output_io.getvalue().splitlines()
    return lines[0] if lines else ""


def run_interactive() -> None:
    print("IMAT-LAB. Press Enter on an empty line to exit.")

    print()
    print("Commands:")
    print("prime(n) ->                                      Test whether n is prime.")
    print("primes(a,b) ->                                   List primes in [a, b).")
    print("factorise(n) ->                                 Factorise n.")
    print(
        "gcd(a,b,...) ->                                  Find the greatest common divisor."
    )
    print(
        "coprime(a,b) ->                                 Test whether a and b are coprime."
    )
    print("pow(a,b,p) ->                                    Calculate a^b modulo p.")
    print(
        "inv(n,p) ->                                      Find the modular inverse of n."
    )
    print(
        "totient(n) ->                                      Calculate Euler's totient."
    )
    print(
        "legendre(n,p) ->                                 Calculate the quadratic-residue symbol."
    )
    print("solve([a1;b1;p1], [a2;b2;p2], ...) ->  Solve a_i x = b_i modulo p_i.")
    print(
        "sqrt(n,p) ->                                     Find the square roots of n modulo p."
    )
    print(
        "quadratic(a,b,c,p) ->                         Solve a x^2 + b x + c = 0 modulo p.\n"
    )
    while True:
        try:
            line = input("IMAT-LAB > ")
        except EOFError:
            break
        if line.strip() == "":
            break
        out = process_line(line, interactive=True)
        if out != "":
            print(out)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_interactive()
    elif len(sys.argv) == 3:
        input_path, output_path = Path(sys.argv[1]), Path(sys.argv[2])
        if input_path.resolve() == output_path.resolve() or (
            output_path.exists() and input_path.samefile(output_path)
        ):
            sys.exit("Input and output must be different files")
        with (
            open(sys.argv[1], "r", encoding="utf-8") as fin,
            open(sys.argv[2], "w", encoding="utf-8") as fout,
        ):
            run_commands(fin, fout)
    else:
        print("Usage: python calculator.py [input.txt output.txt]")

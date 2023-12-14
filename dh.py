
# pylint: disable-all

import sympy
import random


def plain():
    g, p = sympy.randprime(0, 1000), sympy.randprime(0, 1000)
    a, b = random.randint(0, 100), random.randint(0, 100)
    ka, kb = pow(pow(g, b), a) % p, pow(pow(g, a), b) % p
    assert ka == kb
    return ka


def authenticated():
    """TODO: Implement an authenticated version"""


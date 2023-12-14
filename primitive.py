
# pylint: disable-all

import sympy

from argparse import ArgumentParser


def order(g: int, p: int) -> int:
    mods = set()
    for i in range(1, p):
        mods.add(pow(g, i) % p)
    return len(mods)

def primitive(g: int, p: int) -> bool:
    return sympy.is_primitive_root(g, p)


if __name__ == '__main__':
    A = ArgumentParser()
    A.add_argument('-g', '--generator', type=int, help='set generator')
    A.add_argument('-p', '--primitive', type=int, help='primitive value')
    args = A.parse_args()

    args.g, args.p = args.generator, args.primitive
    print('Order of (g=%s, p=%s) = %s' % (args.g, args.p, order(args.g, args.p)))
    print('g=%s is a primitive element for p=%s' % (args.g, args.p) if primitive(args.g, args.p) else
          'g=%s is NOT a primitive element for p=%s' % (args.g, args.p))

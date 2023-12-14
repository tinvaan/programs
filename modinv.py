
# pylint: disable-all

from argparse import ArgumentParser


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


if __name__ == '__main__':
    A = ArgumentParser()
    A.add_argument('--test', help='run tests')
    A.add_argument('-a', type=int, help='first argument')
    A.add_argument('-m', type=int, help='modulus argument')
    args = A.parse_args()

    if args.test:
        assert modinv(5, 7) == pow(5, -1, 7) == 3
    else:
        print('modinv(%s, %s) = %s' % (args.a, args.m, modinv(args.a, args.m)))

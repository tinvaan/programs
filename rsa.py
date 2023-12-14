#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable-all

import contextlib
import random
import sympy


class RSA:
    """
    Generates a public/private key pair where p, q > minPrime
    """
    def gen(self, minPrime: int) -> tuple:
        e = 0
        p, q = sympy.randprime(0, 1000), sympy.randprime(0, 1000)
        n = p * q
        phi = (p - 1) * (q - 1)

        # compute the public exponent
        for e in range(phi):
            with contextlib.suppress(ValueError):
                if sympy.is_primitive_root(e, phi):
                    break

        # compute the private exponent
        d = sympy.mod_inverse(e, phi)
        return ((n, e), (n, d))  # (public key), (private key)


    """
    Encrypts a message using a public key.
    Returns a cipher text message.
    """
    def enc(self, pubKey, msg: int) -> int:
        n, e = pubKey
        return pow(msg, e) % n


    """
    Decrypts a cipher text using a private key.
    Returns a plaintext message.
    """
    def dec(self, privKey, ctxt: int) -> int:
        n, d = privKey
        return pow(ctxt, d) % n


if __name__ == '__main__':
    cipher = RSA()
    msg = random.randint(0, 100)
    pk, pvtk = cipher.gen(sympy.prevprime(50))
    ctxt = cipher.enc(pk, msg)
    print('Original message : %s' % msg)
    print('Encrypted message: %s' % ctxt)
    print('Decrypted message: %s' % cipher.dec(pvtk, ctxt))
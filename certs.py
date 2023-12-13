
# pylint: disable-all

import os
import json
import uuid

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15 as Signature
from datetime import datetime, timedelta



class RegistrationError(Exception):
    def __init__(self, message):
        self.message = message


"""
Typing interfaces
"""
class _Authority:
    def validate(self) -> bool: ...
    def verify(self, pubkey: RSA, signature: tuple) -> tuple: ...
    def register(self, name: str, pubkey: RSA, signature: tuple, force: bool=False) -> object: ...
    def revoke(self, pubkey: RSA) -> object: ...

class _Certificate:
    def is_valid(self) -> bool: ...
    def expired(self) -> bool: ...
    def revoke(self) -> bool: ...
    def register(self, authority: _Authority) -> object: ...



"""
Certificate issuing authority.
"""
class Authority:
    def __init__(self, selfsigned: bool=False) -> None:
        self.id = uuid.uuid4()
        self.certificates = {}
        self.selfsigned = selfsigned

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "Certificate Authority [%s]" % self.id if not self.selfsigned else\
               "Certificate Authority [%s, self-signed]" % self.id

    '''
    Validates all certificates in authority chain
    '''
    def validate(self) -> bool:
        try:
            return all([self.verify(RSA.import_key(pubkey), cert.signature)
                        for (pubkey, cert) in self.certificates.items()])
        except RegistrationError:
            return False

    '''
    Verify given signature using provided public key.
    '''
    def verify(self, pubkey: RsaKey, signature: tuple) -> tuple:
        try:
            Signature.new(pubkey).verify(signature[0], signature[1])
            return signature
        except (ValueError, TypeError):
            raise RegistrationError("Failed to verify signature with public key")

    '''
    Issue and register a new certificate.
    '''
    def register(self, name: str, pubkey: RsaKey, signature: tuple, force=False) -> _Certificate:
        if pubkey.export_key() in self.certificates.keys() and not force:
            raise RegistrationError("Certificate with public key already exists")

        # Validate public key and provided signature
        if self.verify(pubkey, signature):
            # Issue a new certificate and add to certificate records
            self.certificates.update({pubkey.export_key(): Certificate(name, pubkey, signature, issuer=self)})
        return self.certificates.get(pubkey.export_key())

    '''
    Revoke a registered certificate.
    '''
    def revoke(self, pubkey: RsaKey) -> _Certificate:
        if pubkey.export_key() not in self.certificates.keys():
            raise RegistrationError("Certificate with public key not found in authority records")

        certificate = self.certificates.pop(pubkey.export_key())
        certificate.revoke()
        return certificate


"""
Certificate entity.
"""
class Certificate:
    def __init__(self, name: str, pubkey: RsaKey, signature: tuple, issuer: _Authority,
                 subject: str='', expiration: timedelta=timedelta(30), selfsigned: bool=False) -> None:
        self.cid = uuid.uuid4() # certificate id
        self.revoked = False
        self.name = name
        self.subject = subject
        self.issuer = issuer
        self.created = datetime.now()
        self.expiry = self.created + timedelta(365) # default expiry of 1 year
        self.pubkey = pubkey
        self.signature = signature # (message hash, private key signature)
        self.selfsigned = selfsigned

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return json.dumps({'certificate': {
            'name': self.name,
            'issuer': str(self.issuer),
            'created': self.created.isoformat(),
            'expiry': self.expiry.isoformat(),
            'selfsigned': self.selfsigned,
            'pubkey': str(self.pubkey.export_key())
        }}, indent=2)

    @property
    def id(self) -> uuid.uuid4:
        self.cid

    @id.setter
    def id(self, val) -> None:
        self.cid = val

    def is_valid(self) -> bool:
        now = datetime.now()
        return self.created <= now and now >= self.expiry

    def expired(self) -> bool:
        return not self.is_valid()

    def revoke(self) -> bool:
        self.revoked = True

    def register(self, authority: _Authority) -> bool:
        try:
            cert = authority.register(self.name, self.pubkey, self.signature, force=True)

            # Clone the registered certificate properties
            self.id = cert.id
            self.name = cert.name
            self.issuer = cert.issuer
            self.subject = cert.subject
            self.selfsigned = cert.selfsigned
            return True
        except RegistrationError:
            return False


"""
End users of a certificate.
"""
class Domain:
    KEY_SIZE = 2048

    def __init__(self, host: str) -> None:
        self.key = None
        self.hostname = host
        self.nonce = os.urandom(8)

    @property
    def host(self) -> str:
        self.hostname

    '''
    Register a domain with a certificate authority
    '''
    def register(self, authority: _Authority):
        self.key = RSA.generate(self.KEY_SIZE)
        try:
            # Sign a nonce using a private key
            signature = Signature.new(self.key)

            # Register domain with a CA using the corresponding public key
            cert = authority.register(self.hostname, self.key.public_key(),
                                      (SHA256.new(self.nonce), signature.sign(SHA256.new(self.nonce))))

            # Store the registered certificate
            self.certificate = cert
        except (TypeError, ValueError):
            raise RegistrationError('Failed to create certificate for domain "%s"' % self.host)
        return self.certificate

    '''
    Unregsiter domain's certificate
    '''
    def revoke(self, authority: _Authority) -> Certificate:
        cert = authority.revoke(self.certificate.pubkey)
        del self.certificate
        return cert


if __name__ == '__main__':
    rca = Authority(selfsigned=True) # Root CA
    for domain in [Domain('www.apple.com'), Domain('www.facebook.com'), Domain('www.google.com')]:
        domain.register(rca)
        print(domain.certificate, '\n')


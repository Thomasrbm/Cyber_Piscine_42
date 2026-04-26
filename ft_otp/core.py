import os, hmac, hashlib, struct, time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER, SALT_LEN, NONCE_LEN = 600_000, 16, 12


def derive(pw, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())


def hotp(key, counter, digits=6):
    # RFC 4226: HMAC-SHA1, dynamic truncation
    h = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    o = h[-1] & 0xf
    b = ((h[o] & 0x7f) << 24) | (h[o+1] << 16) | (h[o+2] << 8) | h[o+3]
    return f"{b % 10**digits:0{digits}d}"


def totp(key):
    return hotp(key, int(time.time()) // 30)


def is_valid_hex(raw):
    return len(raw) >= 64 and all(c in "0123456789abcdefABCDEF" for c in raw)


def encrypt(secret, pw):
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    ct = AESGCM(derive(pw, salt)).encrypt(nonce, secret, None)
    return salt + nonce + ct


def decrypt(blob, pw):
    salt = blob[:SALT_LEN]
    nonce = blob[SALT_LEN:SALT_LEN+NONCE_LEN]
    ct = blob[SALT_LEN+NONCE_LEN:]
    return AESGCM(derive(pw, salt)).decrypt(nonce, ct, None)

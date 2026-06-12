import hashlib
import hmac
import os
import struct
import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_LEN = 16        # octets aléatoires mélangés au mot de passe
NONCE_LEN = 12       # "number used once" exigé par AES-GCM
ITERATIONS = 600_000


# 6 — vérifie que la clef fait au moins 64 caractères hexadécimaux
def is_valid_hex(text):
    return len(text) >= 64 and all(c in "0123456789abcdefABCDEF" for c in text)


# 7 — transforme le mot de passe en clef AES de 32 octets (PBKDF2, 600k tours)
def derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    return kdf.derive(password.encode())


# 8 — chiffre le secret en AES-GCM, retourne salt + nonce + données chiffrées
def encrypt(secret, password):
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    aes_key = derive_key(password, salt)
    return salt + nonce + AESGCM(aes_key).encrypt(nonce, secret, None)


# 9 — redécoupe salt + nonce + données puis déchiffre (inverse de encrypt)
def decrypt(blob, password):
    salt = blob[:SALT_LEN]
    nonce = blob[SALT_LEN:SALT_LEN + NONCE_LEN]
    data = blob[SALT_LEN + NONCE_LEN:]
    aes_key = derive_key(password, salt)
    return AESGCM(aes_key).decrypt(nonce, data, None)


# 10 — code OTP du moment : le compteur = nombre de tranches de 30s depuis epoch
def totp(secret):
    return hotp(secret, int(time.time()) // 30)


# 11 — RFC 4226 : HMAC-SHA1(secret, compteur) puis extraction de 6 chiffres
def hotp(secret, counter, digits=6):
    mac = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F                       # 4 bits de poids faible = position
    code = int.from_bytes(mac[offset:offset + 4], "big") & 0x7FFFFFFF
    return f"{code % 10 ** digits:0{digits}d}"

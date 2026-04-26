import os, hmac, hashlib, struct, time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER, SALT_LEN, NONCE_LEN = 600_000, 16, 12


# hash
# fait 600k sha256
# padding 32
# appel la vraie fonction dans le .derive
def derive(password, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())


# counteur = le nombre de tranches de 30sec depuis epoch
def hotp(secret, counter, digits=6):
    # la norme RFC 4226 impose big endian, 64bits,
    # struct empact le chiffre de temps comme ça
    counter_bytes = struct.pack(">Q", counter)

    # hmac = creé un hash avec 1 clef + une valeure (ici le temps)
    mac = hmac.new(secret, counter_bytes, hashlib.sha1).digest()
    # donne 20 bytes

    # garde les 4 bits les plus a droite du hmac de 20 bytes
    offset = mac[-1] & 0x0f

    # 4 octet à partir de l'offset
    chunk = mac[offset:offset+4]
    # int big endiant du chunk de 4 ( donne un nombre int)
    raw = int.from_bytes(chunk, "big")
    # annule le bit de signe pour forcer le chiffre à être positif
    code = raw & 0x7fffffff

    # nombre modulo 1000000 (10 puissance 6)
    # garde que 6 dernier chiffres de droites
    temp_code = code % 10**digits
    return f"{temp_code:0{digits}d}"


def totp(secret):
    return hotp(secret, int(time.time()) // 30)


def is_valid_hex(raw):
    return len(raw) >= 64 and all(c in "0123456789abcdefABCDEF" for c in raw)


# hexa en secret + mdp d'input
def encrypt(secret, password):
    # salt random de 16 byte
    # Nonce de 12 random
    # (nonce = number used once, clef aléatoire pour le chiffrement)
    salt = os.urandom(16)
    nonce = os.urandom(12)
    # crée un clef  AES avec le mdp (clef =c le hash)
    aes_key = derive(password, salt)
    cipher = AESGCM(aes_key)
    # chiffre la clef avec AES
    ciphertext = cipher.encrypt(nonce, secret, None)
    return salt + nonce + ciphertext  # concat


def decrypt(ciphertext, password):
    salt = ciphertext[:SALT_LEN]
    nonce = ciphertext[SALT_LEN:SALT_LEN+NONCE_LEN]
    ct = ciphertext[SALT_LEN+NONCE_LEN:]
    aes_key = derive(password, salt)
    cipher = AESGCM(aes_key)
    return cipher.decrypt(nonce, ct, None)

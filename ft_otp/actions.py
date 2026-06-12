import base64
import os

import qrcode

from utils import totp, encrypt, decrypt, is_valid_hex


# 2 — écrit une clef hexa aléatoire de 64 caractères dans un fichier
def new_hex_key(path):
    open(path, "w").write(os.urandom(32).hex())
    return f"Random hex key saved to {path}"


# 3 — "-g" : chiffre la clef hexa avec le mot de passe, sauve dans ft_otp.key
def save_key(hex_path, password):
    hex_key = open(hex_path).read().strip()
    if not is_valid_hex(hex_key):
        raise ValueError("key must be 64 hexadecimal characters")

    open("ft_otp.key", "wb").write(encrypt(bytes.fromhex(hex_key), password))
    os.chmod("ft_otp.key", 0o600)
    return "Key was successfully saved in ft_otp.key."


# 4 — "-k" : déchiffre le fichier .key et retourne le code OTP du moment
def make_otp(key_path, password):
    secret = decrypt(open(key_path, "rb").read(), password)
    return totp(secret)


# 5 — "-q" : clef hexa → base32 → URI otpauth → QR code en png
def save_qr(hex_path):
    hex_key = open(hex_path).read().strip()
    secret = base64.b32encode(bytes.fromhex(hex_key)).decode().rstrip("=")
    qrcode.make(f"otpauth://totp/ft_otp:user?secret={secret}&issuer=ft_otp").save("ft_otp.png")
    return "QR code saved to ft_otp.png"

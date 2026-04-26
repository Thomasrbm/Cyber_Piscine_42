import os, sys, base64, getpass
from core import totp, encrypt, decrypt, is_valid_hex


def store(path):
    raw = open(path).read().strip()
    if not is_valid_hex(raw):
        sys.exit("./ft_otp: error: key must be 64 hexadecimal characters.")
    pw = getpass.getpass("Passphrase: ")
    open("ft_otp.key", "wb").write(encrypt(bytes.fromhex(raw), pw))
    os.chmod("ft_otp.key", 0o600)
    print("Key was successfully saved in ft_otp.key.")


def generate(path):
    blob = open(path, "rb").read()
    pw = getpass.getpass("Passphrase: ")
    try:
        key = decrypt(blob, pw)
    except Exception:
        sys.exit("./ft_otp: error: invalid passphrase or corrupted key file.")
    print(totp(key))


def qr(path):
    import qrcode
    raw = open(path).read().strip()
    secret = base64.b32encode(bytes.fromhex(raw)).decode().rstrip("=")
    uri = f"otpauth://totp/ft_otp:user?secret={secret}&issuer=ft_otp"
    qrcode.make(uri).save("ft_otp.png")
    print("QR code saved to ft_otp.png")

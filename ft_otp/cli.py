import os, sys, base64, getpass
from current.Cyber_Piscine_42.ft_otp.utils import totp, encrypt, decrypt, is_valid_hex


# prend un fichier avec une clef hexa 64len
# crée avec un fichier .key cypher
def store(path):
    raw = open(path).read().strip()  # lit sans \n
    if not is_valid_hex(raw):
        sys.exit("./ft_otp: error: key must be 64 hexadecimal characters.")
    # lit depuis stdin sans afficher input dans le terminal : input() modif
    password = getpass.getpass("Passphrase: ")
    # bytes builtin python, d'un hexa fait obj byte
    open("ft_otp.key", "wb").write(encrypt(bytes.fromhex(raw), password))
    os.chmod("ft_otp.key", 0o600)
    print("Key was successfully saved in ft_otp.key.")


def generate(path):
    ciphertext = open(path, "rb").read()
    password = getpass.getpass("Passphrase: ")
    try:
        secret = decrypt(ciphertext, password)
    except Exception:
        sys.exit("./ft_otp: error: invalid passphrase or corrupted key file.")
    print(totp(secret))


def qr(path):
    import qrcode
    raw = open(path).read().strip()
    secret_bytes = bytes.fromhex(raw)              # hex → 32 octets bruts
    base32_bytes = base64.b32encode(secret_bytes)          # 32 octets → bytes Base32
    base32_string = base32_bytes.decode()                  # bytes → string
    base32_secret = base32_string.rstrip("=")              # enlève le padding
    # content meta data + le secret a mettre en qr
    uri = f"otpauth://totp/ft_otp:user?secret={base32_secret}&issuer=ft_otp"
    qrcode.make(uri).save("ft_otp.png")
    print("QR code saved to ft_otp.png")

# otpauth://totp/ft_otp:user?secret=GEZDGN...&issuer=ft_otp
#    │      │       │           │              │
#    │      │       │           │              └── nom de l'app dans Authenticator
#    │      │       │           └── le secret en Base32
#    │      │       └── label affiché : "ft_otp:user"
#    │      └── type d'OTP : totp (vs hotp)
#    └── schéma de l'URI

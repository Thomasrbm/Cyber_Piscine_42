#!/usr/bin/env python3
import argparse
import getpass
import sys

from cryptography.exceptions import InvalidTag

from actions import save_key, make_otp, save_qr
from gui import run_gui


# 1 — point d'entrée : parse les options et appelle la bonne action
def main():
    parser = argparse.ArgumentParser(prog="./ft_otp")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("-g", metavar="hexfile", help="chiffre la clef hexa dans ft_otp.key")
    action.add_argument("-k", metavar="keyfile", help="affiche le code OTP du moment")
    action.add_argument("-q", metavar="hexfile", help="génère un QR code (ft_otp.png)")
    action.add_argument("-i", metavar="keyfile", nargs="?", const="ft_otp.key",
                        help="ouvre l'interface graphique")
    args = parser.parse_args()

    try:
        if args.i:
            run_gui(args.i)
        elif args.g:
            print(save_key(args.g, getpass.getpass("Passphrase: ")))
        elif args.k:
            print(make_otp(args.k, getpass.getpass("Passphrase: ")))
        elif args.q:
            print(save_qr(args.q))
    except OSError as e:
        sys.exit(f"./ft_otp: error: {e.strerror}: '{e.filename}'")
    except InvalidTag:
        sys.exit("./ft_otp: error: invalid passphrase or corrupted key file.")
    except ValueError:
        sys.exit("./ft_otp: error: key must be 64 hexadecimal characters.")


if __name__ == "__main__":
    main()

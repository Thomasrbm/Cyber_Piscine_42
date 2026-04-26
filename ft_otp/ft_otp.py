#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "-i":
        from gui import run
        run(sys.argv[2] if len(sys.argv) == 3 else "ft_otp.key")
        return
    if len(sys.argv) != 3 or sys.argv[1] not in ("-g", "-k", "-q"):
        sys.exit("usage: ./ft_otp -g <hexkey> | -k <ft_otp.key> | -q <hexkey> | -i [ft_otp.key]")
    from cli import store, generate, qr
    try:
        {"-g": store, "-k": generate, "-q": qr}[sys.argv[1]](sys.argv[2])
    except OSError as e:
        sys.exit(f"./ft_otp: error: {e.strerror}: '{e.filename}'")
    except ValueError:
        sys.exit("./ft_otp: error: key must be 64 hexadecimal characters.")


if __name__ == "__main__":
    main()

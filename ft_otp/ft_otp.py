#!/usr/bin/env python3
# permet de fait ./
import sys


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "-i":
        from current.Cyber_Piscine_42.ft_otp.gui import run
        run(sys.argv[2] if len(sys.argv) == 3 else "ft_otp.key")
        # si ./ft_otp -i use ft_otp.key sinon le truc passé en arg
        return

    if len(sys.argv) != 3 or sys.argv[1] not in ("-g", "-k", "-q"):
        sys.exit("usage: ./ft_otp -g <hexkey> \
                 | -k <ft_otp.key> | -q <hexkey> \
                 | -i [ft_otp.key]")

    from current.Cyber_Piscine_42.ft_otp.cli import store, generate, qr
    try:
        flag = sys.argv[1]
        arg = sys.argv[2]
        if flag == "-g":
            store(arg)
        elif flag == "-k":
            generate(arg)
        elif flag == "-q":
            qr(arg)
    except OSError as e:
        sys.exit(f"./ft_otp: error: {e.strerror}: '{e.filename}'")
    except ValueError:
        sys.exit("./ft_otp: error: key must be 64 hexadecimal characters.")


if __name__ == "__main__":
    main()

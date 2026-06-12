import tkinter as tk
from tkinter import ttk, messagebox

from actions import new_hex_key, save_key, make_otp, save_qr
from widgets import make_section, make_field, make_button


# 12 — "-i" : fenêtre principale, une section par action
def run_gui(key_path="ft_otp.key"):
    window = tk.Tk()
    window.title("ft_otp")

    genkey_section(window)
    store_section(window)
    otp_section(window, key_path)
    qr_section(window)

    window.mainloop()


# 13 — lance une action et affiche son résultat (ou l'erreur) en popup
def popup(action, *args):
    try:
        messagebox.showinfo("ft_otp", action(*args))
    except Exception as error:
        messagebox.showerror("ft_otp", str(error))


# 14 — section : génère une clef hexa aléatoire dans un fichier
def genkey_section(window):
    frame = make_section(window, "Generate hex key")
    output = make_field(frame, "Output file:", 0, default="key.hex")
    make_button(frame, "Generate", 1, lambda: popup(new_hex_key, output.get()))


# 15 — section "-g" : chiffre la clef hexa dans ft_otp.key
def store_section(window):
    frame = make_section(window, "Store key (-g)")
    hex_file = make_field(frame, "Hex key:", 0, picker=True)
    password = make_field(frame, "Passphrase:", 1, mask="*")
    make_button(frame, "Store", 2, lambda: popup(save_key, hex_file.get(), password.get()))


# 16 — section "-k" : affiche le code OTP en grand
def otp_section(window, key_path):
    frame = make_section(window, "Generate OTP (-k)")
    key_file = make_field(frame, "Key file:", 0, default=key_path, picker=True)
    password = make_field(frame, "Passphrase:", 1, mask="*")

    display = ttk.Label(frame, text="------", font=("monospace", 22))
    display.grid(row=2, column=0, columnspan=3, pady=4)

    def show_otp():
        try:
            display.config(text=make_otp(key_file.get(), password.get()))
        except Exception:
            display.config(text="invalid")

    make_button(frame, "Generate", 3, show_otp)


# 17 — section "-q" : QR code depuis la clef hexa
def qr_section(window):
    frame = make_section(window, "QR code (-q)")
    hex_file = make_field(frame, "Hex key:", 0, picker=True)
    make_button(frame, "Make QR", 1, lambda: popup(save_qr, hex_file.get()))

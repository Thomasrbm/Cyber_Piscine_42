import os, base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from current.Cyber_Piscine_42.ft_otp.utils import totp, encrypt, decrypt, is_valid_hex


def make_field(parent_frame, label_text, row, mask_char=None, default_value="", with_file_picker=False):

    # le text, dans la frame du module courrant
    # 0, 0 row colone + sticky w = aligne a gauche + espace autour
    ttk.Label(parent_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=4, pady=2)

    # show=None par defaut  écrit ce  que tu tape, mais si * aurait mit * comme mdp
    entry = ttk.Entry(parent_frame, width=30, show=mask_char)
    entry.grid(row=row, column=1, padx=4, pady=2)  # juste a droite colonne 1 met l'entry

    if default_value:
        entry.insert(0, default_value)
    # met parfois text préremplit si défault value

    # bouton parcourir
    if with_file_picker:
        def pick_file():
            # vide tout le champs
            entry.delete(0, "end")
            # insert ce que choisit dans askopen (ouvre nav de fichier)
            entry.insert(0, filedialog.askopenfilename())
        # crée bouton ... pour activier le pickfile
        ttk.Button(parent_frame, text="...", width=3, command=pick_file).grid(row=row, column=2, padx=2)

    return entry


def genkey_section(window):
    section_frame = ttk.LabelFrame(window, text="Generate hex key", padding=8)
    # fill x = occupue toute la largeur
    section_frame.pack(fill="x", padx=8, pady=4)

    output_file_entry = make_field(section_frame, "Output file:", 0, default_value="key.hex")

    def on_generate_click():
        try:
            output_path = output_file_entry.get()  # lit ce que dans champs (file)
            random_hex = os.urandom(32).hex()  # 32 byte en 64char hex
            open(output_path, "w").write(random_hex)  # met l hex dedans
            messagebox.showinfo("ft_otp", f"Random hex key saved to {output_path}")
        except Exception as error:
            messagebox.showerror("ft_otp", str(error))

    ttk.Button(section_frame, text="Generate", command=on_generate_click).grid(row=1, column=1, sticky="e", pady=4)


def store_section(window):
    section_frame = ttk.LabelFrame(window, text="Store key (-g)", padding=8)
    section_frame.pack(fill="x", padx=8, pady=4)

    hex_key_entry = make_field(section_frame, "Hex key:", 0, with_file_picker=True)
    passphrase_entry = make_field(section_frame, "Passphrase:", 1, mask_char="*")

    def on_store_click():
        try:
            hex_content = open(hex_key_entry.get()).read().strip()
            # lit le fichier .key sans \n

            if not is_valid_hex(hex_content):
                raise ValueError("key must be 64 hexadecimal characters")

            secret_bytes = bytes.fromhex(hex_content)  # met en bytes
            passphrase = passphrase_entry.get()  # choppe le mdp
            encrypted_blob = encrypt(secret_bytes, passphrase)  # encrypt le

            open("ft_otp.key", "wb").write(encrypted_blob)
            os.chmod("ft_otp.key", 0o600)

            messagebox.showinfo("ft_otp", "Key saved to ft_otp.key")
        except Exception as error:
            messagebox.showerror("ft_otp", str(error))

    ttk.Button(section_frame, text="Store", command=on_store_click).grid(row=2, column=1, sticky="e", pady=4)


def generate_section(window, default_key_path="ft_otp.key"):
    section_frame = ttk.LabelFrame(window, text="Generate OTP (-k)", padding=8)
    section_frame.pack(fill="x", padx=8, pady=4)

    key_file_entry = make_field(section_frame, "Key file:", 0, with_file_picker=True, default_value=default_key_path)
    passphrase_entry = make_field(section_frame, "Passphrase:", 1, mask_char="*")

    # le _ _ _ _ pour les chiffres
    otp_display = ttk.Label(section_frame, text="------", font=("monospace", 22))
    otp_display.grid(row=2, column=0, columnspan=3, pady=4)

    def on_generate_click():
        try:
            encrypted_blob = open(key_file_entry.get(), "rb").read()
            passphrase = passphrase_entry.get()
            secret_key = decrypt(encrypted_blob, passphrase)

            otp_display.config(text=totp(secret_key))
        except Exception:
            otp_display.config(text="invalid")

    ttk.Button(section_frame, text="Generate", command=on_generate_click).grid(row=3, column=1, sticky="e", pady=4)


def qr_section(window):
    section_frame = ttk.LabelFrame(window, text="QR code (-q)", padding=8)
    section_frame.pack(fill="x", padx=8, pady=4)

    hex_key_entry = make_field(section_frame, "Hex key:", 0, with_file_picker=True)

    def on_make_qr_click():
        try:
            import qrcode

            hex_content = open(hex_key_entry.get()).read().strip()
            base32_secret = base64.b32encode(bytes.fromhex(hex_content)).decode().rstrip("=")
            otpauth_uri = f"otpauth://totp/ft_otp:user?secret={base32_secret}&issuer=ft_otp"

            qrcode.make(otpauth_uri).save("ft_otp.png")
            messagebox.showinfo("ft_otp", "QR saved to ft_otp.png")
        except Exception as error:
            messagebox.showerror("ft_otp", str(error))

    ttk.Button(section_frame, text="Make QR", command=on_make_qr_click).grid(row=1, column=1, sticky="e", pady=4)


def run(key_path="ft_otp.key"):
    window = tk.Tk()
    window.title("ft_otp")

    genkey_section(window)
    store_section(window)
    generate_section(window, default_key_path=key_path)
    qr_section(window)

    window.mainloop()

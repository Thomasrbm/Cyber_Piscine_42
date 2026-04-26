import os, base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import totp, encrypt, decrypt, is_valid_hex


def field(parent, label, row, show=None, default="", with_pick=False):
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
    e = ttk.Entry(parent, width=30, show=show)
    e.grid(row=row, column=1, padx=4, pady=2)
    if default:
        e.insert(0, default)
    if with_pick:
        ttk.Button(parent, text="...", width=3,
                   command=lambda: (e.delete(0, "end"), e.insert(0, filedialog.askopenfilename()))).grid(row=row, column=2, padx=2)
    return e


def genkey_section(root):
    f = ttk.LabelFrame(root, text="Generate hex key", padding=8)
    f.pack(fill="x", padx=8, pady=4)
    e_out = field(f, "Output file:", 0, default="key.hex")

    def action():
        try:
            open(e_out.get(), "w").write(os.urandom(32).hex())
            messagebox.showinfo("ft_otp", f"Random hex key saved to {e_out.get()}")
        except Exception as ex:
            messagebox.showerror("ft_otp", str(ex))
    ttk.Button(f, text="Generate", command=action).grid(row=1, column=1, sticky="e", pady=4)


def store_section(root):
    f = ttk.LabelFrame(root, text="Store key (-g)", padding=8)
    f.pack(fill="x", padx=8, pady=4)
    e_key = field(f, "Hex key:", 0, with_pick=True)
    e_pw = field(f, "Passphrase:", 1, show="*")

    def action():
        try:
            raw = open(e_key.get()).read().strip()
            if not is_valid_hex(raw):
                raise ValueError("key must be 64 hexadecimal characters")
            open("ft_otp.key", "wb").write(encrypt(bytes.fromhex(raw), e_pw.get()))
            os.chmod("ft_otp.key", 0o600)
            messagebox.showinfo("ft_otp", "Key saved to ft_otp.key")
        except Exception as ex:
            messagebox.showerror("ft_otp", str(ex))
    ttk.Button(f, text="Store", command=action).grid(row=2, column=1, sticky="e", pady=4)


def generate_section(root, default_key="ft_otp.key"):
    f = ttk.LabelFrame(root, text="Generate OTP (-k)", padding=8)
    f.pack(fill="x", padx=8, pady=4)
    e_key = field(f, "Key file:", 0, with_pick=True, default=default_key)
    e_pw = field(f, "Passphrase:", 1, show="*")
    out = ttk.Label(f, text="------", font=("monospace", 22))
    out.grid(row=2, column=0, columnspan=3, pady=4)

    def action():
        try:
            key = decrypt(open(e_key.get(), "rb").read(), e_pw.get())
            out.config(text=totp(key))
        except Exception:
            out.config(text="invalid")
    ttk.Button(f, text="Generate", command=action).grid(row=3, column=1, sticky="e", pady=4)


def qr_section(root):
    f = ttk.LabelFrame(root, text="QR code (-q)", padding=8)
    f.pack(fill="x", padx=8, pady=4)
    e_key = field(f, "Hex key:", 0, with_pick=True)

    def action():
        try:
            import qrcode
            raw = open(e_key.get()).read().strip()
            secret = base64.b32encode(bytes.fromhex(raw)).decode().rstrip("=")
            uri = f"otpauth://totp/ft_otp:user?secret={secret}&issuer=ft_otp"
            qrcode.make(uri).save("ft_otp.png")
            messagebox.showinfo("ft_otp", "QR saved to ft_otp.png")
        except Exception as ex:
            messagebox.showerror("ft_otp", str(ex))
    ttk.Button(f, text="Make QR", command=action).grid(row=1, column=1, sticky="e", pady=4)


def run(key_path="ft_otp.key"):
    root = tk.Tk()
    root.title("ft_otp")
    genkey_section(root)
    store_section(root)
    generate_section(root, default_key=key_path)
    qr_section(root)
    root.mainloop()

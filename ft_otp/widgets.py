from tkinter import ttk, filedialog


# 18 — cadre avec titre, sur toute la largeur de la fenêtre
def make_section(window, title):
    frame = ttk.LabelFrame(window, text=title, padding=8)
    frame.pack(fill="x", padx=8, pady=4)
    return frame


# 19 — ligne "label + champ de saisie" (+ bouton "..." si picker)
def make_field(frame, label, row, mask=None, default="", picker=False):
    ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)

    entry = ttk.Entry(frame, width=30, show=mask)
    entry.grid(row=row, column=1, padx=4, pady=2)
    entry.insert(0, default)

    if picker:
        def pick_file():
            entry.delete(0, "end")
            entry.insert(0, filedialog.askopenfilename())
        ttk.Button(frame, text="...", width=3, command=pick_file).grid(row=row, column=2, padx=2)

    return entry


# 20 — bouton d'action aligné à droite de la section
def make_button(frame, text, row, command):
    ttk.Button(frame, text=text, command=command).grid(row=row, column=1, sticky="e", pady=4)

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ------------------------------
# 1️⃣ Databáze SQLite
# ------------------------------
conn = sqlite3.connect("pujcovna.db")
cursor = conn.cursor()

# Tabulka strojů
cursor.execute("""
CREATE TABLE IF NOT EXISTS stroje (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev TEXT NOT NULL,
    popis TEXT,
    cena_za_den REAL NOT NULL,
    dostupnost TEXT CHECK(dostupnost IN ('Ano', 'Ne')) NOT NULL
)
""")

# Tabulka klientů
cursor.execute("""
CREATE TABLE IF NOT EXISTS klienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev_firmy TEXT NOT NULL,
    adresa TEXT,
    ico TEXT,
    sleva REAL DEFAULT 0,
    kontakt TEXT
)
""")

# ------------------------------
# 2️⃣ Ukázková data
# ------------------------------
cursor.execute("SELECT COUNT(*) FROM stroje")
if cursor.fetchone()[0] == 0:
    cursor.executemany("""
        INSERT INTO stroje (nazev, popis, cena_za_den, dostupnost)
        VALUES (?, ?, ?, ?)
    """, [
        ("Bagr CAT 320", "Velký pásový bagr s lopatou 1.2 m³", 5000, "Ano"),
        ("Minibagr Kubota", "Malý bagr vhodný pro zahradní práce", 2500, "Ano"),
        ("Jeřáb Liebherr", "Věžový jeřáb, výška 30 m", 8500, "Ne"),
        ("Nakladač JCB 435S", "Čelní nakladač s lopatou 3 m³", 4200, "Ano"),
        ("Sklápěč Tatra 815", "Nákladní auto s korbou 20 m³", 3700, "Ne"),
        ("Válcovač Hamm HD 12", "Vibrační válec pro hutnění", 2900, "Ano")
    ])

cursor.execute("SELECT COUNT(*) FROM klienti")
if cursor.fetchone()[0] == 0:
    cursor.executemany("""
        INSERT INTO klienti (nazev_firmy, adresa, ico, sleva, kontakt)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ("Stavmont s.r.o.", "Praha 4, Na Dlouhé 25", "12345678", 10, "Jan Novák"),
        ("Zemstav Brno a.s.", "Brno, Vídeňská 114", "87654321", 5, "Petr Svoboda"),
        ("BauPartner CZ", "Ostrava, Hlavní 45", "99887766", 7, "Lucie Hlaváčková"),
        ("InstaStav", "Plzeň, Rokycanská 201", "55443322", 12, "Tomáš Jelínek")
    ])
conn.commit()

# ------------------------------
# 3️⃣ Funkce aplikace
# ------------------------------
def aktualizovat_data():
    cursor.execute("SELECT nazev_firmy FROM klienti")
    klienti = [row[0] for row in cursor.fetchall()]
    klient_combobox["values"] = klienti

    cursor.execute("SELECT nazev, dostupnost FROM stroje")
    stroje = cursor.fetchall()
    stroj_combobox["values"] = [s[0] for s in stroje]

    stroj_barvy.clear()
    for nazev, dostupnost in stroje:
        stroj_barvy[nazev] = "green" if dostupnost == "Ano" else "red"

def vypocitat_cenu():
    klient = klient_combobox.get()
    stroj = stroj_combobox.get()
    dny = dny_entry.get()

    if not klient or not stroj or not dny:
        messagebox.showwarning("Chyba", "Vyplňte všechna pole.")
        return

    try:
        dny = int(dny)
    except ValueError:
        messagebox.showwarning("Chyba", "Počet dní musí být číslo.")
        return

    cursor.execute("SELECT sleva FROM klienti WHERE nazev_firmy=?", (klient,))
    sleva = cursor.fetchone()
    sleva = sleva[0] if sleva else 0

    cursor.execute("SELECT cena_za_den FROM stroje WHERE nazev=?", (stroj,))
    cena = cursor.fetchone()
    if not cena:
        messagebox.showerror("Chyba", "Vybraný stroj nebyl nalezen.")
        return

    celkem = dny * cena[0] * (1 - sleva / 100)
    vysledek_label.config(text=f"Celková cena: {celkem:,.2f} Kč")

def pridat_stroj():
    novy_stroj = (nazev_entry.get(), popis_entry.get(), cena_entry.get(), dostupnost_var.get())
    if not all(novy_stroj):
        messagebox.showwarning("Chyba", "Vyplňte všechna pole pro nový stroj.")
        return
    try:
        float(novy_stroj[2])
    except ValueError:
        messagebox.showwarning("Chyba", "Cena musí být číslo.")
        return

    cursor.execute("INSERT INTO stroje (nazev, popis, cena_za_den, dostupnost) VALUES (?, ?, ?, ?)", novy_stroj)
    conn.commit()
    aktualizovat_data()
    messagebox.showinfo("OK", "Stroj byl přidán.")
    nazev_entry.delete(0, tk.END)
    popis_entry.delete(0, tk.END)
    cena_entry.delete(0, tk.END)

def pridat_klienta():
    novy_klient = (firma_entry.get(), adresa_entry.get(), ico_entry.get(), sleva_entry.get(), kontakt_entry.get())
    if not all(novy_klient):
        messagebox.showwarning("Chyba", "Vyplňte všechna pole pro nového klienta.")
        return
    try:
        float(novy_klient[3])
    except ValueError:
        messagebox.showwarning("Chyba", "Sleva musí být číslo.")
        return

    cursor.execute("INSERT INTO klienti (nazev_firmy, adresa, ico, sleva, kontakt) VALUES (?, ?, ?, ?, ?)", novy_klient)
    conn.commit()
    aktualizovat_data()
    messagebox.showinfo("OK", "Klient byl přidán.")
    firma_entry.delete(0, tk.END)
    adresa_entry.delete(0, tk.END)
    ico_entry.delete(0, tk.END)
    sleva_entry.delete(0, tk.END)
    kontakt_entry.delete(0, tk.END)

def zmen_barvu_stroje(event):
    stroj = stroj_combobox.get()
    if stroj in stroj_barvy:
        barva = stroj_barvy[stroj]
        stroj_combobox.configure(foreground=barva)

# ------------------------------
# 4️⃣ GUI
# ------------------------------
root = tk.Tk()
root.title("Půjčovna stavebních strojů")
root.geometry("700x600")
root.configure(bg="#f2f2f2")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 11), background="#f2f2f2")
style.configure("TButton", font=("Arial", 11, "bold"))
style.configure("TCombobox", font=("Arial", 11))
style.configure("TEntry", font=("Arial", 11))

stroj_barvy = {}

# --- Výběr klienta a stroje ---
ttk.Label(root, text="Klient:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
klient_combobox = ttk.Combobox(root, state="readonly")
klient_combobox.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(root, text="Stroj:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
stroj_combobox = ttk.Combobox(root, state="readonly")
stroj_combobox.grid(row=1, column=1, padx=10, pady=10)
stroj_combobox.bind("<<ComboboxSelected>>", zmen_barvu_stroje)

ttk.Label(root, text="Počet dní:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
dny_entry = ttk.Entry(root)
dny_entry.grid(row=2, column=1, padx=10, pady=10)

ttk.Button(root, text="💰 Vypočítat cenu", command=vypocitat_cenu).grid(row=3, column=0, columnspan=2, pady=10)
vysledek_label = ttk.Label(root, text="", font=("Arial", 14, "bold"))
vysledek_label.grid(row=4, column=0, columnspan=2, pady=10)

# --- Přidání nového stroje ---
ttk.Label(root, text="--- Přidat nový stroj ---").grid(row=5, column=0, columnspan=2, pady=15)

nazev_entry = ttk.Entry(root)
popis_entry = ttk.Entry(root)
cena_entry = ttk.Entry(root)
dostupnost_var = tk.StringVar(value="Ano")

ttk.Radiobutton(root, text="Dostupný", variable=dostupnost_var, value="Ano").grid(row=6, column=0)
ttk.Radiobutton(root, text="Nedostupný", variable=dostupnost_var, value="Ne").grid(row=6, column=1)

ttk.Label(root, text="Název:").grid(row=7, column=0, sticky="e")
nazev_entry.grid(row=7, column=1, pady=2)
ttk.Label(root, text="Popis:").grid(row=8, column=0, sticky="e")
popis_entry.grid(row=8, column=1, pady=2)
ttk.Label(root, text="Cena/den:").grid(row=9, column=0, sticky="e")
cena_entry.grid(row=9, column=1, pady=2)
ttk.Button(root, text="➕ Přidat stroj", command=pridat_stroj).grid(row=10, column=0, columnspan=2, pady=10)

# --- Přidání nového klienta ---
ttk.Label(root, text="--- Přidat nového klienta ---").grid(row=11, column=0, columnspan=2, pady=15)
firma_entry = ttk.Entry(root)
adresa_entry = ttk.Entry(root)
ico_entry = ttk.Entry(root)
sleva_entry = ttk.Entry(root)
kontakt_entry = ttk.Entry(root)

labels = ["Firma:", "Adresa:", "IČO:", "Sleva (%):", "Kontakt:"]
entries = [firma_entry, adresa_entry, ico_entry, sleva_entry, kontakt_entry]
for i, (lbl, ent) in enumerate(zip(labels, entries), start=12):
    ttk.Label(root, text=lbl).grid(row=i, column=0, sticky="e")
    ent.grid(row=i, column=1, pady=2)

ttk.Button(root, text="➕ Přidat klienta", command=pridat_klienta).grid(row=17, column=0, columnspan=2, pady=10)

aktualizovat_data()
root.mainloop()

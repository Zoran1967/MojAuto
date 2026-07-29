"""
Database modul - SQLite konekcija i upiti.

Tabele:
- prodavnice (id, naziv)
- proizvodi (id, naziv, jedinica_mere, zadnja_cena, prodavnica_id,
             kategorija_id, podkategorija_id, podrazumevana_kolicina)
- kategorije (id, naziv, roditelj_id)  - roditelj_id NULL = glavna kategorija,
             roditelj_id postavljen = podkategorija te glavne kategorije
- liste (id, datum, prodavnica_id, ukupno, zatvorena)
- lista_stavke (id, lista_id, proizvod_id, naziv, kolicina, cena_po_jedinici, total)
- podesavanja (kljuc, vrednost)

Napomena o valutama: sve cene se u bazi CUVAJU UVEK U RSD (bazna valuta).
Prikaz i unos se preracunavaju u letu prema trenutno izabranoj valuti
(funkcije rsd_u_prikaz / prikaz_u_rsd na dnu fajla).

Napomena o vise lista: aplikacija moze imati vise ISTOVREMENO OTVORENIH
(zatvorena=0) lista, po jednu po prodavnici. Lista postaje deo istorije
tek kad korisnik eksplicitno pritisne "Snimi racun" (close_lista).
Dok je otvorena, lista se NE racuna u istoriju (get_istorija /
get_prodavnice_sa_istorijom vraД‡aju samo zatvorena=1).
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_db_path():
    try:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "shopping.db")
    except ImportError:
        return os.path.join(BASE_DIR, "shopping.db")


DB_PATH = _get_db_path()

SEED_PO_KATEGORIJI = {
    "Voce": [
        ("Jabuka", "kg"), ("Kruska", "kg"), ("Banana", "kg"), ("Pomorandza", "kg"),
        ("Limun", "kg"), ("Mandarina", "kg"), ("Grozdje", "kg"), ("Jagoda", "kg"),
        ("Malina", "kg"), ("Kupina", "kg"), ("Borovnica", "kg"), ("Lubenica", "kg"),
        ("Dinja", "kg"), ("Kajsija", "kg"), ("Breskva", "kg"), ("Nektarina", "kg"),
        ("Sljiva", "kg"), ("Visnja", "kg"), ("Tresnja", "kg"), ("Kivi", "kg"),
        ("Ananas", "kom"), ("Nar", "kg"), ("Grejpfrut", "kg"), ("Avokado", "kom"),
        ("Mango", "kom"), ("Suve smokve", "kg"), ("Suve kajsije", "kg"), ("Datule", "kg"),
    ],
    "Povrce": [
        ("Krompir", "kg"), ("Luk crni", "kg"), ("Beli luk", "kg"), ("Paradajz", "kg"),
        ("Krastavac", "kg"), ("Paprika babura", "kg"), ("Paprika ljuta", "kg"),
        ("Sargarepa", "kg"), ("Kupus", "kg"), ("Kiseli kupus", "kg"), ("Karfiol", "kg"),
        ("Brokoli", "kg"), ("Tikvice", "kg"), ("Patlidzan", "kg"), ("Spanac", "kg"),
        ("Zelena salata", "kom"), ("Praziluk", "kg"), ("Celer", "kg"), ("Persun", "vez"),
        ("Cvekla", "kg"), ("Pasulj svez", "kg"), ("Grasak svez", "kg"), ("Kukuruz secerac", "kom"),
        ("Rotkvice", "vez"), ("Tikva", "kg"), ("Bundeva", "kg"), ("Sampinjoni", "kg"),
        ("Vrganji", "kg"),
    ],
    "Meso": [
        ("Piletina belo meso", "kg"), ("Piletina batak i krilca", "kg"), ("Piletina cela", "kg"),
        ("Juneci biftek", "kg"), ("Juneci mleveni", "kg"), ("Juneci but", "kg"),
        ("Svinjski kare", "kg"), ("Svinjska plecka", "kg"), ("Svinjski but", "kg"),
        ("Cevapi", "kg"), ("Pljeskavice", "kg"), ("Kobasice domace", "kg"),
        ("Slanina", "kg"), ("Prsuta", "kg"), ("Cureci file", "kg"), ("Jagnjetina", "kg"),
        ("Mleveno meso mesano", "kg"), ("Rebarca", "kg"), ("Dimljena slanina", "kg"),
    ],
    "Riba": [
        ("Losos file", "kg"), ("Skusa", "kg"), ("Sardina sveza", "kg"),
        ("Oslic file", "kg"), ("Pastrmka", "kg"),
        ("Skampi", "kg"), ("Lignje", "kg"), ("Dagnje", "kg"), ("Bakalar", "kg"),
    ],
    "Mlecni proizvodi": [
        ("Mleko", "l"), ("Jogurt", "kom"), ("Kisela pavlaka", "kom"), ("Slatka pavlaka", "kom"),
        ("Sir", "kg"), ("Kajmak", "kg"), ("Puter", "kom"), ("Svezi sir", "kg"),
        ("Feta sir", "kg"), ("Kefir", "kom"), ("Cheddar sir", "kom"), ("Mocarela", "kom"),
        ("Parmezan", "kom"), ("Skuta", "kom"), ("Trapist sir", "kg"), ("Gauda sir", "kg"),
        ("Kondenzovano mleko", "kom"),
    ],
    "Hleb i peciva": [
        ("Hleb beli", "kom"), ("Hleb crni", "kom"), ("Hleb integralni", "kom"),
        ("Lepinja", "kom"), ("Somun", "kom"), ("Kifla", "kom"), ("Perece", "kom"),
        ("Burek sa mesom", "kom"), ("Burek sa sirom", "kom"), ("Pita zeljanica", "kom"),
        ("Tost hleb", "kom"), ("Zemicke", "kom"), ("Djevrek", "kom"), ("Vekna", "kom"),
        ("Kroasan", "kom"),
    ],
    "Testenine": [
        ("Spagete", "kg"), ("Makarone", "kg"), ("Rezanci", "kg"), ("Fusili", "kg"),
        ("Njoki", "kg"), ("Lazanje", "kom"), ("Testenina za supu", "kg"), ("Penne", "kg"),
    ],
    "Pirinac": [
        ("Pirinac beli", "kg"), ("Pirinac integralni", "kg"), ("Basmati pirinac", "kg"),
        ("Pirinac za rizoto", "kg"),
    ],
    "Konzervirana hrana": [
        ("Grasak konzerva", "kom"), ("Kukuruz konzerva", "kom"), ("Pasulj konzerva", "kom"),
        ("Tunjevina konzerva", "kom"), ("Paradajz pasirani", "kom"), ("Ajvar", "kom"),
        ("Kisele krastavice", "kom"), ("Kisela paprika", "kom"), ("Turcija mesana", "kom"),
        ("Pecurke konzerva", "kom"), ("Pasta od paradajza", "kom"), ("Kiseli kupus konzerva", "kom"),
    ],
    "Grickalice": [
        ("Cips", "kom"), ("Kikiriki", "kg"), ("Kokice", "kom"), ("Slani stapici", "kom"),
        ("Krekeri", "kom"), ("Bademi", "kg"), ("Lesnici", "kg"), ("Suvo grozdje", "kg"),
        ("Pistaci", "kg"), ("Indijski orascici", "kg"), ("Susene banane", "kg"),
    ],
    "Slatkisi": [
        ("Cokolada mlecna", "kom"), ("Cokolada crna", "kom"), ("Keks", "kom"),
        ("Vafli", "kom"), ("Bombone", "kom"), ("Zvake", "kom"), ("Sladoled", "kom"),
        ("Kolac", "kom"), ("Torta", "kom"), ("Med", "kom"), ("Napolitanke", "kom"),
        ("Cokoladni namaz", "kom"), ("Marshmallow", "kom"),
    ],
    "Bezalkoholna pica": [
        ("Kola", "kom"), ("Fanta", "kom"), ("Sprite", "kom"), ("Limunada", "kom"),
        ("Ledeni caj", "kom"), ("Tonik", "kom"), ("Energetsko pice", "kom"),
    ],
    "Sokovi": [
        ("Sok od pomorandze", "kom"), ("Sok od jabuke", "kom"), ("Sok od breskve", "kom"),
        ("Multivitaminski sok", "kom"), ("Nektar od kajsije", "kom"), ("Cedjeni sok", "kom"),
    ],
    "Voda": [
        ("Negazirana voda", "kom"), ("Gazirana voda", "kom"), ("Mineralna voda", "kom"),
        ("Izvorska voda 5l", "kom"),
    ],
    "Kafa": [
        ("Kafa mlevena", "kom"), ("Kafa u zrnu", "kom"), ("Instant kafa", "kom"),
        ("Kapsule za kafu", "kom"), ("Turska kafa", "kom"), ("Espreso kafa", "kom"),
    ],
    "Caj": [
        ("Crni caj", "kom"), ("Zeleni caj", "kom"), ("Vocni caj", "kom"),
        ("Kamilica", "kom"), ("Nana caj", "kom"), ("Djumbir caj", "kom"),
    ],
    "Alkoholna pica": [
        ("Pivo", "kom"), ("Vino crveno", "kom"), ("Vino belo", "kom"),
        ("Rakija sljivovica", "kom"), ("Viski", "kom"), ("Votka", "kom"), ("Gin", "kom"),
    ],
    "Zamrznuti proizvodi": [
        ("Zamrznuto povrce mesano", "kg"), ("Zamrznuto voce mesano", "kg"),
        ("Pomfrit smrznuti", "kg"), ("Sladoled porodicno pakovanje", "kom"),
        ("Riblji stapici", "kom"), ("Pica smrznuta", "kom"), ("Zamrznuti spanac", "kg"),
        ("Zamrznuta piletina", "kg"), ("Burek smrznuti", "kom"),
    ],
    "Sredstva za ciscenje": [
        ("Deterdzent za ves", "kom"), ("Deterdzent za sudove", "kom"),
        ("Sredstvo za pod", "kom"), ("Sredstvo za staklo", "kom"), ("Omeksivac", "kom"),
        ("Belilo", "kom"), ("Sundjeri za sudove", "kom"), ("Kese za smece", "kom"),
        ("Toalet papir", "kom"), ("Kuhinjski ubrusi", "kom"), ("Sredstvo za wc", "kom"),
        ("Sredstvo protiv kamenca", "kom"), ("Krpe za ciscenje", "kom"),
    ],
    "Kozmetika": [
        ("Sampon", "kom"), ("Balzam za kosu", "kom"), ("Krema za lice", "kom"),
        ("Krema za ruke", "kom"), ("Dezodorans", "kom"), ("Parfem", "kom"),
        ("Losion za telo", "kom"), ("Regenerator za kosu", "kom"), ("Maska za lice", "kom"),
        ("Krema za suncanje", "kom"),
    ],
    "Higijena": [
        ("Pasta za zube", "kom"), ("Cetkica za zube", "kom"), ("Sapun", "kom"),
        ("Higijenski ulosci", "kom"), ("Vlazne maramice", "kom"), ("Brijac", "kom"),
        ("Pena za brijanje", "kom"), ("Konac za zube", "kom"), ("Tecni sapun", "kom"),
        ("Papirne maramice", "kom"),
    ],
    "Hrana za kucne ljubimce": [
        ("Hrana za pse suva", "kg"), ("Hrana za pse konzerva", "kom"),
        ("Hrana za macke suva", "kg"), ("Hrana za macke konzerva", "kom"),
        ("Pesak za macke", "kom"), ("Poslastice za pse", "kom"), ("Poslastice za macke", "kom"),
    ],
    "Decija hrana": [
        ("Kasica vocna", "kom"), ("Kasica povrtna", "kom"), ("Mleko za bebe", "kom"),
        ("Pelene", "kom"), ("Vlazne maramice za bebe", "kom"), ("Decija hrana konzerva", "kom"),
        ("Keksici za bebe", "kom"), ("Cajevi za bebe", "kom"),
    ],
}

SEED_KATEGORIJE = [
    "Voce", "Povrce", "Meso", "Riba", "Mlecni proizvodi", "Hleb i peciva",
    "Testenine", "Pirinac", "Konzervirana hrana", "Grickalice", "Slatkisi",
    "Bezalkoholna pica", "Sokovi", "Voda", "Kafa", "Caj", "Alkoholna pica",
    "Zamrznuti proizvodi", "Sredstva za ciscenje", "Kozmetika", "Higijena",
    "Hrana za kucne ljubimce", "Decija hrana",
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _kolone_tabele(c, tabela):
    c.execute(f"PRAGMA table_info({tabela})")
    return {red[1] for red in c.fetchall()}


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS prodavnice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT UNIQUE NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS proizvodi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT UNIQUE NOT NULL,
        jedinica_mere TEXT NOT NULL,
        zadnja_cena REAL DEFAULT 0,
        prodavnica_id INTEGER,
        FOREIGN KEY (prodavnica_id) REFERENCES prodavnice(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS liste (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT NOT NULL,
        prodavnica_id INTEGER,
        ukupno REAL DEFAULT 0,
        zatvorena INTEGER DEFAULT 0,
        FOREIGN KEY (prodavnica_id) REFERENCES prodavnice(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS lista_stavke (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lista_id INTEGER NOT NULL,
        proizvod_id INTEGER NOT NULL,
        naziv TEXT NOT NULL,
        kolicina REAL NOT NULL,
        cena_po_jedinici REAL NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (lista_id) REFERENCES liste(id),
        FOREIGN KEY (proizvod_id) REFERENCES proizvodi(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS podesavanja (
        kljuc TEXT PRIMARY KEY,
        vrednost TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS kategorije (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT NOT NULL,
        roditelj_id INTEGER,
        UNIQUE(naziv, roditelj_id),
        FOREIGN KEY (roditelj_id) REFERENCES kategorije(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cene_po_prodavnici (
        proizvod_id INTEGER NOT NULL,
        prodavnica_id INTEGER NOT NULL,
        cena REAL NOT NULL,
        datum TEXT,
        PRIMARY KEY (proizvod_id, prodavnica_id),
        FOREIGN KEY (proizvod_id) REFERENCES proizvodi(id),
        FOREIGN KEY (prodavnica_id) REFERENCES prodavnice(id)
    )""")
    conn.commit()

    # --- Migracija: dodavanje novih kolona na POSTOJECU proizvodi tabelu,
    # bez brisanja ijednog reda - postojeci podaci ostaju netaknuti. ---
    kolone = _kolone_tabele(c, "proizvodi")
    if "kategorija_id" not in kolone:
        c.execute("ALTER TABLE proizvodi ADD COLUMN kategorija_id INTEGER")
    if "podkategorija_id" not in kolone:
        c.execute("ALTER TABLE proizvodi ADD COLUMN podkategorija_id INTEGER")
    if "podrazumevana_kolicina" not in kolone:
        c.execute("ALTER TABLE proizvodi ADD COLUMN podrazumevana_kolicina REAL")
    conn.commit()

    # --- Seed kategorija PRVO (proizvodi se oslanjaju na njihove id-jeve) ---
    c.execute("SELECT COUNT(*) FROM kategorije")
    kategorije_prazne = c.fetchone()[0] == 0
    if kategorije_prazne:
        c.executemany(
            "INSERT INTO kategorije (naziv, roditelj_id) VALUES (?, NULL)",
            [(naziv,) for naziv in SEED_PO_KATEGORIJI],
        )
        conn.commit()

    # --- Seed proizvoda, svaki povezan sa svojom kategorijom, BEZ cene i
    # BEZ podrazumevane kolicine (korisnik sam popunjava kad kupuje) ---
    c.execute("SELECT COUNT(*) FROM proizvodi")
    if c.fetchone()[0] == 0:
        kategorija_id_po_nazivu = dict(
            c.execute("SELECT naziv, id FROM kategorije WHERE roditelj_id IS NULL").fetchall()
        )
        redovi = []
        for kategorija_naziv, proizvodi_liste in SEED_PO_KATEGORIJI.items():
            kat_id = kategorija_id_po_nazivu.get(kategorija_naziv)
            for naziv, jedinica in proizvodi_liste:
                redovi.append((naziv, jedinica, kat_id))
        c.executemany(
            "INSERT INTO proizvodi (naziv, jedinica_mere, zadnja_cena, prodavnica_id, "
            "kategorija_id, podkategorija_id, podrazumevana_kolicina) "
            "VALUES (?, ?, 0, NULL, ?, NULL, NULL)",
            redovi,
        )
        conn.commit()

    conn.close()


# ---------- Prodavnice ----------

def get_prodavnice():
    conn = get_connection()
    rows = conn.execute("SELECT id, naziv FROM prodavnice ORDER BY naziv").fetchall()
    conn.close()
    return rows


def get_prva_prodavnica():
    """Prva prodavnica uneta u bazu (po redosledu dodavanja). None ako nema nijedne."""
    conn = get_connection()
    row = conn.execute("SELECT id, naziv FROM prodavnice ORDER BY id LIMIT 1").fetchone()
    conn.close()
    return row


def add_prodavnica(naziv):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM prodavnice WHERE LOWER(naziv) = LOWER(?)", (naziv,))
    row = c.fetchone()
    if row:
        conn.close()
        return row[0]
    c.execute("INSERT INTO prodavnice (naziv) VALUES (?)", (naziv,))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def update_prodavnica(prodavnica_id, novi_naziv):
    """Preimenuje prodavnicu. Vraca False ako vec postoji prodavnica sa tim imenom."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id FROM prodavnice WHERE LOWER(naziv) = LOWER(?) AND id != ?",
        (novi_naziv, prodavnica_id),
    )
    if c.fetchone():
        conn.close()
        return False
    c.execute("UPDATE prodavnice SET naziv = ? WHERE id = ?", (novi_naziv, prodavnica_id))
    conn.commit()
    conn.close()
    return True


def delete_prodavnica(prodavnica_id):
    """
    Brise prodavnicu trajno. Vraca False ako je koriscena u nekoj listi
    (otvorenoj ili zatvorenoj) ili je vezana za neki proizvod - u tom
    slucaju se ne brise, da se ne pokvari istorija ili baza proizvoda.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM liste WHERE prodavnica_id = ?", (prodavnica_id,))
    if c.fetchone()[0] > 0:
        conn.close()
        return False
    c.execute("SELECT COUNT(*) FROM proizvodi WHERE prodavnica_id = ?", (prodavnica_id,))
    if c.fetchone()[0] > 0:
        conn.close()
        return False
    c.execute("DELETE FROM prodavnice WHERE id = ?", (prodavnica_id,))
    conn.commit()
    conn.close()
    return True


# ---------- Kategorije i podkategorije ----------

def get_kategorije(roditelj_id=None):
    """Vraca (id, naziv). roditelj_id=None -> glavne kategorije.
    roditelj_id=<broj> -> podkategorije te kategorije."""
    conn = get_connection()
    if roditelj_id is None:
        rows = conn.execute(
            "SELECT id, naziv FROM kategorije WHERE roditelj_id IS NULL ORDER BY naziv"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, naziv FROM kategorije WHERE roditelj_id = ? ORDER BY naziv",
            (roditelj_id,),
        ).fetchall()
    conn.close()
    return rows


def get_kategorija_naziv(kategorija_id):
    if kategorija_id is None:
        return None
    conn = get_connection()
    row = conn.execute("SELECT naziv FROM kategorije WHERE id = ?", (kategorija_id,)).fetchone()
    conn.close()
    return row[0] if row else None


def add_kategorija(naziv, roditelj_id=None):
    conn = get_connection()
    c = conn.cursor()
    if roditelj_id is None:
        c.execute(
            "SELECT id FROM kategorije WHERE LOWER(naziv) = LOWER(?) AND roditelj_id IS NULL",
            (naziv,),
        )
    else:
        c.execute(
            "SELECT id FROM kategorije WHERE LOWER(naziv) = LOWER(?) AND roditelj_id = ?",
            (naziv, roditelj_id),
        )
    row = c.fetchone()
    if row:
        conn.close()
        return row[0]
    c.execute("INSERT INTO kategorije (naziv, roditelj_id) VALUES (?, ?)", (naziv, roditelj_id))
    conn.commit()
    kid = c.lastrowid
    conn.close()
    return kid


def update_kategorija(kategorija_id, novi_naziv):
    """Vraca False ako vec postoji kategorija/podkategorija sa tim imenom na istom nivou."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT roditelj_id FROM kategorije WHERE id = ?", (kategorija_id,))
    red = c.fetchone()
    if not red:
        conn.close()
        return False
    roditelj_id = red[0]
    if roditelj_id is None:
        c.execute(
            "SELECT id FROM kategorije WHERE LOWER(naziv) = LOWER(?) "
            "AND roditelj_id IS NULL AND id != ?",
            (novi_naziv, kategorija_id),
        )
    else:
        c.execute(
            "SELECT id FROM kategorije WHERE LOWER(naziv) = LOWER(?) "
            "AND roditelj_id = ? AND id != ?",
            (novi_naziv, roditelj_id, kategorija_id),
        )
    if c.fetchone():
        conn.close()
        return False
    c.execute("UPDATE kategorije SET naziv = ? WHERE id = ?", (novi_naziv, kategorija_id))
    conn.commit()
    conn.close()
    return True


def delete_kategorija(kategorija_id):
    """
    Brise kategoriju/podkategoriju. Vraca False ako:
    - ima podkategorija (za glavnu kategoriju), ili
    - je koriscena kod nekog proizvoda (kao kategorija ili podkategorija).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM kategorije WHERE roditelj_id = ?", (kategorija_id,))
    if c.fetchone()[0] > 0:
        conn.close()
        return False
    c.execute(
        "SELECT COUNT(*) FROM proizvodi WHERE kategorija_id = ? OR podkategorija_id = ?",
        (kategorija_id, kategorija_id),
    )
    if c.fetchone()[0] > 0:
        conn.close()
        return False
    c.execute("DELETE FROM kategorije WHERE id = ?", (kategorija_id,))
    conn.commit()
    conn.close()
    return True


# ---------- Proizvodi ----------

def search_proizvodi(query, limit=8):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, naziv, jedinica_mere, zadnja_cena FROM proizvodi "
        "WHERE LOWER(naziv) LIKE ? ORDER BY naziv LIMIT ?",
        (f"%{query.lower()}%", limit),
    ).fetchall()
    conn.close()
    return rows


def get_proizvodi_sa_prodavnicom():
    """Nepromenjeno (kompatibilnost): (id, naziv, jedinica_mere, zadnja_cena,
    naziv_prodavnice, prodavnica_id)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.id, p.naziv, p.jedinica_mere, p.zadnja_cena,
                  COALESCE(pr.naziv, '-'), p.prodavnica_id
           FROM proizvodi p
           LEFT JOIN prodavnice pr ON p.prodavnica_id = pr.id
           ORDER BY p.naziv"""
    ).fetchall()
    conn.close()
    return rows


def get_proizvodi_puno():
    """Isto kao get_proizvodi_sa_prodavnicom, plus kategorija/podkategorija
    id i naziv i podrazumevana kolicina. Vraca:
    (id, naziv, jedinica_mere, zadnja_cena, prodavnica_naziv, prodavnica_id,
     kategorija_id, kategorija_naziv, podkategorija_id, podkategorija_naziv,
     podrazumevana_kolicina)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.id, p.naziv, p.jedinica_mere, p.zadnja_cena,
                  COALESCE(pr.naziv, '-'), p.prodavnica_id,
                  p.kategorija_id, k.naziv,
                  p.podkategorija_id, pk.naziv,
                  p.podrazumevana_kolicina
           FROM proizvodi p
           LEFT JOIN prodavnice pr ON p.prodavnica_id = pr.id
           LEFT JOIN kategorije k ON p.kategorija_id = k.id
           LEFT JOIN kategorije pk ON p.podkategorija_id = pk.id
           ORDER BY p.naziv"""
    ).fetchall()
    conn.close()
    return rows


def add_or_update_proizvod(naziv, jedinica_mere, cena, prodavnica_id=None,
                            kategorija_id=None, podkategorija_id=None,
                            podrazumevana_kolicina=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM proizvodi WHERE LOWER(naziv) = LOWER(?)", (naziv,))
    row = c.fetchone()
    if row:
        pid = row[0]
        c.execute(
            "UPDATE proizvodi SET zadnja_cena = ?, jedinica_mere = ?, "
            "prodavnica_id = COALESCE(?, prodavnica_id), "
            "kategorija_id = COALESCE(?, kategorija_id), "
            "podkategorija_id = COALESCE(?, podkategorija_id), "
            "podrazumevana_kolicina = COALESCE(?, podrazumevana_kolicina) "
            "WHERE id = ?",
            (cena, jedinica_mere, prodavnica_id, kategorija_id,
             podkategorija_id, podrazumevana_kolicina, pid),
        )
    else:
        c.execute(
            "INSERT INTO proizvodi (naziv, jedinica_mere, zadnja_cena, prodavnica_id, "
            "kategorija_id, podkategorija_id, podrazumevana_kolicina) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (naziv, jedinica_mere, cena, prodavnica_id, kategorija_id,
             podkategorija_id, podrazumevana_kolicina),
        )
        pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid


def update_proizvod(proizvod_id, naziv, jedinica_mere, cena, prodavnica_id=None,
                     kategorija_id=None, podkategorija_id=None,
                     podrazumevana_kolicina=None):
    """
    Eksplicitna izmena - postavlja TACNO poslate vrednosti za prodavnica_id/
    kategorija_id/podkategorija_id/podrazumevana_kolicina (None = "bez",
    eksplicitno brise vezu, za razliku od add_or_update_proizvod koji cuva
    staru vrednost ako se ne posalje nova).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id FROM proizvodi WHERE LOWER(naziv) = LOWER(?) AND id != ?",
        (naziv, proizvod_id),
    )
    if c.fetchone():
        conn.close()
        return False
    c.execute(
        "UPDATE proizvodi SET naziv = ?, jedinica_mere = ?, zadnja_cena = ?, "
        "prodavnica_id = ?, kategorija_id = ?, podkategorija_id = ?, "
        "podrazumevana_kolicina = ? WHERE id = ?",
        (naziv, jedinica_mere, cena, prodavnica_id, kategorija_id,
         podkategorija_id, podrazumevana_kolicina, proizvod_id),
    )
    conn.commit()
    conn.close()
    return True


def delete_proizvod(proizvod_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM lista_stavke WHERE proizvod_id = ?", (proizvod_id,))
    if c.fetchone()[0] > 0:
        conn.close()
        return False
    c.execute("DELETE FROM proizvodi WHERE id = ?", (proizvod_id,))
    conn.commit()
    conn.close()
    return True


# ---------- Liste za kupovinu (podrska za VISE istovremeno otvorenih) ----------

def create_lista(prodavnica_id):
    conn = get_connection()
    c = conn.cursor()
    datum = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.execute(
        "INSERT INTO liste (datum, prodavnica_id, ukupno, zatvorena) VALUES (?, ?, 0, 0)",
        (datum, prodavnica_id),
    )
    conn.commit()
    lista_id = c.lastrowid
    conn.close()
    return lista_id


def get_otvorene_liste():
    """Sve trenutno otvorene (nezatvorene) liste, sa nazivom prodavnice.
    Vraca [(lista_id, prodavnica_id, prodavnica_naziv), ...]."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT l.id, l.prodavnica_id, COALESCE(pr.naziv, 'Bez prodavnice')
           FROM liste l
           LEFT JOIN prodavnice pr ON l.prodavnica_id = pr.id
           WHERE l.zatvorena = 0
           ORDER BY l.id"""
    ).fetchall()
    conn.close()
    return rows


def get_or_create_otvorena_lista(prodavnica_id):
    """Vraca lista_id postojece otvorene liste za tu prodavnicu, ili
    pravi novu ako ne postoji."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM liste WHERE prodavnica_id = ? AND zatvorena = 0 LIMIT 1",
        (prodavnica_id,),
    ).fetchone()
    conn.close()
    if row:
        return row[0]
    return create_lista(prodavnica_id)


def add_stavka(lista_id, proizvod_id, naziv, kolicina, cena_po_jedinici):
    total = kolicina * cena_po_jedinici
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO lista_stavke (lista_id, proizvod_id, naziv, kolicina, "
        "cena_po_jedinici, total) VALUES (?, ?, ?, ?, ?, ?)",
        (lista_id, proizvod_id, naziv, kolicina, cena_po_jedinici, total),
    )
    conn.commit()
    conn.close()
    return total


def get_stavke_sa_id(lista_id):
    """Kao get_lista_stavke, ali sa id stavke - potrebno za izmenu/brisanje/
    pomeranje pojedinacne stavke. Vraca (id, naziv, kolicina,
    cena_po_jedinici, total, proizvod_id)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, naziv, kolicina, cena_po_jedinici, total, proizvod_id
           FROM lista_stavke WHERE lista_id = ? ORDER BY id""",
        (lista_id,),
    ).fetchall()
    conn.close()
    return rows


def _obrisi_ako_prazna_otvorena_lista(lista_id):
    """Ciscenje: ako otvorena (nezatvorena) lista ostane bez ijedne
    stavke (npr. posle brisanja/pomeranja poslednje stavke), obrisi je
    da se ne gomilaju prazne liste. Zatvorene liste (istorija) se
    NIKAD ne diraju ovde."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT zatvorena FROM liste WHERE id = ?", (lista_id,))
    red = c.fetchone()
    if not red or red[0] == 1:
        conn.close()
        return
    c.execute("SELECT COUNT(*) FROM lista_stavke WHERE lista_id = ?", (lista_id,))
    if c.fetchone()[0] == 0:
        c.execute("DELETE FROM liste WHERE id = ?", (lista_id,))
        conn.commit()
    conn.close()


def update_stavka(stavka_id, kolicina, cena_po_jedinici):
    """Menja kolicinu i/ili cenu jedne stavke u otvorenoj listi.
    NE dira proizvodi tabelu (samo ova konkretna stavka na listi)."""
    total = kolicina * cena_po_jedinici
    conn = get_connection()
    conn.execute(
        "UPDATE lista_stavke SET kolicina = ?, cena_po_jedinici = ?, total = ? WHERE id = ?",
        (kolicina, cena_po_jedinici, total, stavka_id),
    )
    conn.commit()
    conn.close()
    return total


def delete_stavka(stavka_id):
    """Brise SAMO stavku sa liste kupovine. NIKAD ne brise proizvod iz
    baze proizvoda (tabela proizvodi ostaje netaknuta)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT lista_id FROM lista_stavke WHERE id = ?", (stavka_id,))
    row = c.fetchone()
    c.execute("DELETE FROM lista_stavke WHERE id = ?", (stavka_id,))
    conn.commit()
    conn.close()
    if row:
        _obrisi_ako_prazna_otvorena_lista(row[0])


def move_stavka_prodavnica(stavka_id, nova_prodavnica_id):
    """Premesta stavku u (otvorenu) listu druge prodavnice. Ako stara
    lista ostane prazna, brise se (samo ako je i dalje otvorena)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT lista_id FROM lista_stavke WHERE id = ?", (stavka_id,))
    row = c.fetchone()
    stara_lista_id = row[0] if row else None
    conn.close()

    nova_lista_id = get_or_create_otvorena_lista(nova_prodavnica_id)

    conn = get_connection()
    conn.execute(
        "UPDATE lista_stavke SET lista_id = ? WHERE id = ?", (nova_lista_id, stavka_id)
    )
    conn.commit()
    conn.close()

    if stara_lista_id and stara_lista_id != nova_lista_id:
        _obrisi_ako_prazna_otvorena_lista(stara_lista_id)

    return nova_lista_id


def close_lista(lista_id, ukupno):
    conn = get_connection()
    conn.execute(
        "UPDATE liste SET ukupno = ?, zatvorena = 1 WHERE id = ?",
        (ukupno, lista_id),
    )
    conn.commit()
    conn.close()


def get_istorija():
    conn = get_connection()
    rows = conn.execute(
        """SELECT l.datum, COALESCE(pr.naziv, 'Bez prodavnice'), l.ukupno
           FROM liste l
           LEFT JOIN prodavnice pr ON l.prodavnica_id = pr.id
           WHERE l.zatvorena = 1
           ORDER BY l.id DESC"""
    ).fetchall()
    conn.close()
    return rows


def get_prodavnice_sa_istorijom():
    conn = get_connection()
    rows = conn.execute(
        """SELECT pr.id, pr.naziv, COUNT(l.id)
           FROM liste l
           JOIN prodavnice pr ON l.prodavnica_id = pr.id
           WHERE l.zatvorena = 1
           GROUP BY pr.id, pr.naziv
           ORDER BY pr.naziv"""
    ).fetchall()
    conn.close()
    return rows


def get_liste_za_prodavnicu(prodavnica_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, datum, ukupno FROM liste
           WHERE prodavnica_id = ? AND zatvorena = 1
           ORDER BY id DESC""",
        (prodavnica_id,),
    ).fetchall()
    conn.close()
    return rows


def get_lista_stavke(lista_id):
    """Nepromenjeno (koristi history_screen.py) - bez id stavke."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT naziv, kolicina, cena_po_jedinici, total
           FROM lista_stavke WHERE lista_id = ? ORDER BY id""",
        (lista_id,),
    ).fetchall()
    conn.close()
    return rows


def delete_lista(lista_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM lista_stavke WHERE lista_id = ?", (lista_id,))
    c.execute("DELETE FROM liste WHERE id = ?", (lista_id,))
    conn.commit()
    conn.close()


# ---------- Podesavanja ----------

def get_setting(kljuc, default=None):
    conn = get_connection()
    row = conn.execute(
        "SELECT vrednost FROM podesavanja WHERE kljuc = ?", (kljuc,)
    ).fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(kljuc, vrednost):
    conn = get_connection()
    conn.execute(
        "INSERT INTO podesavanja (kljuc, vrednost) VALUES (?, ?) "
        "ON CONFLICT(kljuc) DO UPDATE SET vrednost = excluded.vrednost",
        (kljuc, vrednost),
    )
    conn.commit()
    conn.close()


# ---------- Konverzija valuta ----------

def get_valuta():
    return get_setting("valuta", "RSD")


def get_kurs():
    try:
        return float(get_setting("kurs", "117.5"))
    except (TypeError, ValueError):
        return 117.5


def rsd_u_prikaz(cena_rsd):
    if get_valuta() == "EUR":
        return cena_rsd / get_kurs()
    return cena_rsd


def prikaz_u_rsd(cena_prikaz):
    if get_valuta() == "EUR":
        return cena_prikaz * get_kurs()
    return cena_prikaz


def valuta_oznaka():
    return "в‚¬" if get_valuta() == "EUR" else "din"


# ---------- Cene po prodavnicama (istorija/poredjenje) ----------

def zabelezi_cenu_za_prodavnicu(proizvod_id, prodavnica_id, cena_rsd):
    """Pamti/azurira poslednju poznatu cenu ovog proizvoda za TU
    konkretnu prodavnicu (uvek u RSD). Poziva se svaki put kad se
    proizvod doda na listu ili se cena stavke izmeni."""
    if prodavnica_id is None:
        return
    conn = get_connection()
    datum = datetime.now().strftime("%d.%m.%Y %H:%M")
    conn.execute(
        "INSERT INTO cene_po_prodavnici (proizvod_id, prodavnica_id, cena, datum) "
        "VALUES (?, ?, ?, ?) "
        "ON CONFLICT(proizvod_id, prodavnica_id) DO UPDATE SET cena = excluded.cena, datum = excluded.datum",
        (proizvod_id, prodavnica_id, cena_rsd, datum),
    )
    conn.commit()
    conn.close()


def get_cena_za_prodavnicu(proizvod_id, prodavnica_id):
    """Poslednja zabelezena cena (RSD) za ovaj proizvod u TOJ prodavnici,
    ili None ako jos nije zabelezena."""
    if proizvod_id is None or prodavnica_id is None:
        return None
    conn = get_connection()
    row = conn.execute(
        "SELECT cena FROM cene_po_prodavnici WHERE proizvod_id = ? AND prodavnica_id = ?",
        (proizvod_id, prodavnica_id),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_sve_cene_proizvoda(proizvod_id):
    """Sve poznate cene ovog proizvoda po SVIM prodavnicama, za
    poredjenje ("gde je jeftinije"). Vraca [(prodavnica_naziv, cena_rsd, datum), ...]
    sortirano od najjeftinije ka najskupljoj."""
    if proizvod_id is None:
        return []
    conn = get_connection()
    rows = conn.execute(
        """SELECT pr.naziv, cp.cena, cp.datum
           FROM cene_po_prodavnici cp
           JOIN prodavnice pr ON cp.prodavnica_id = pr.id
           WHERE cp.proizvod_id = ?
           ORDER BY cp.cena ASC""",
        (proizvod_id,),
    ).fetchall()
    conn.close()
    return rows

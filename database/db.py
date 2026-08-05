"""
Database modul - SQLite konekcija i upiti za MojAuto aplikaciju.

Tabele:
- vozila, gorivo, servisi, ulje, filteri, gume, registracija,
  osiguranje, akumulator, kvarovi, troskovi, dokumenti, podsetnici
- podesavanja (kljuc, vrednost) - koristi je tema aplikacije, NE DIRATI
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_db_path():
    try:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "mojauto.db")
    except ImportError:
        return os.path.join(BASE_DIR, "mojauto.db")


DB_PATH = _get_db_path()

SCHEMA = {
    "vozila": """
        CREATE TABLE IF NOT EXISTS vozila (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marka TEXT NOT NULL,
            model TEXT NOT NULL,
            godina INTEGER,
            registracija TEXT,
            vin TEXT,
            broj_sasije TEXT,
            broj_motora TEXT,
            gorivo TEXT,
            zapremina REAL,
            snaga INTEGER,
            menjac TEXT,
            boja TEXT,
            datum_kupovine TEXT,
            kupovna_cena REAL,
            kilometraza INTEGER DEFAULT 0,
            napomena TEXT,
            broj_vrata INTEGER
        );
    """,
    "gorivo": """
        CREATE TABLE IF NOT EXISTS gorivo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            vreme TEXT,
            kilometraza INTEGER NOT NULL,
            pumpa TEXT,
            grad TEXT,
            litara REAL NOT NULL,
            cena_po_litru REAL NOT NULL,
            ukupna_cena REAL NOT NULL,
            pun_rezervoar INTEGER DEFAULT 1,
            napomena TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "servisi": """
        CREATE TABLE IF NOT EXISTS servisi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            tip TEXT NOT NULL,
            datum TEXT NOT NULL,
            kilometraza INTEGER,
            naziv TEXT,
            opis TEXT,
            cena_delova REAL DEFAULT 0,
            cena_rada REAL DEFAULT 0,
            ukupna_cena REAL DEFAULT 0,
            fotografije TEXT,
            racun TEXT,
            napomena TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "ulje": """
        CREATE TABLE IF NOT EXISTS ulje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            marka TEXT,
            vrsta TEXT,
            gradacija TEXT,
            kolicina REAL,
            cena REAL,
            datum TEXT,
            kilometraza INTEGER,
            sledeca_zamena INTEGER,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "filteri": """
        CREATE TABLE IF NOT EXISTS filteri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            tip TEXT NOT NULL,
            cena REAL,
            datum TEXT,
            kilometraza INTEGER,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "gume": """
        CREATE TABLE IF NOT EXISTS gume (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            sezona TEXT NOT NULL,
            marka TEXT,
            model TEXT,
            dimenzija TEXT,
            dot TEXT,
            cena REAL,
            datum_kupovine TEXT,
            kilometraza_montaze INTEGER,
            napomena TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "registracija": """
        CREATE TABLE IF NOT EXISTS registracija (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            datum_registracije TEXT,
            istek TEXT,
            cena REAL,
            tehnicki_pregled TEXT,
            napomena TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "osiguranje": """
        CREATE TABLE IF NOT EXISTS osiguranje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            vrsta TEXT,
            cena REAL,
            datum TEXT,
            istek TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "akumulator": """
        CREATE TABLE IF NOT EXISTS akumulator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            marka TEXT,
            model TEXT,
            kapacitet TEXT,
            datum_kupovine TEXT,
            cena REAL,
            garancija TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "kvarovi": """
        CREATE TABLE IF NOT EXISTS kvarovi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            kilometraza INTEGER,
            opis TEXT,
            cena_rada REAL DEFAULT 0,
            cena_delova REAL DEFAULT 0,
            ukupna_cena REAL DEFAULT 0,
            fotografije TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "troskovi": """
        CREATE TABLE IF NOT EXISTS troskovi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            vrsta TEXT NOT NULL,
            iznos REAL NOT NULL,
            datum TEXT NOT NULL,
            napomena TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "dokumenti": """
        CREATE TABLE IF NOT EXISTS dokumenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            tip TEXT NOT NULL,
            naziv TEXT,
            putanja TEXT NOT NULL,
            datum_dodavanja TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "podsetnici": """
        CREATE TABLE IF NOT EXISTS podsetnici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            tip TEXT NOT NULL,
            naslov TEXT,
            datum_isteka TEXT,
            kilometraza_isteka INTEGER,
            aktivan INTEGER DEFAULT 1,
            FOREIGN KEY (vehicle_id) REFERENCES vozila (id) ON DELETE CASCADE
        );
    """,
    "podesavanja": """
        CREATE TABLE IF NOT EXISTS podesavanja (
            kljuc TEXT PRIMARY KEY,
            vrednost TEXT
        );
    """,
}


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
    for tabela_sql in SCHEMA.values():
        c.execute(tabela_sql)
    conn.commit()

    # --- Migracija: dodavanje nove kolone na POSTOJECU vozila tabelu,
    # bez brisanja ijednog postojeceg vozila. ---
    kolone = _kolone_tabele(c, "vozila")
    if "broj_vrata" not in kolone:
        c.execute("ALTER TABLE vozila ADD COLUMN broj_vrata INTEGER")
    conn.commit()

    conn.close()


# ---------- Generisane CRUD funkcije (rade za sve tabele) ----------

def insert(table, data: dict):
    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    values = tuple(data.values())
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    novi_id = c.lastrowid
    conn.close()
    return novi_id


def update(table, record_id, data: dict):
    set_clause = ", ".join(f"{key} = ?" for key in data.keys())
    values = tuple(data.values()) + (record_id,)
    conn = get_connection()
    conn.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete(table, record_id):
    conn = get_connection()
    conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def get_by_id(table, record_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return row


def get_all(table, order_by="id"):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    conn.close()
    return rows


def get_by_vehicle(table, vehicle_id, order_by="id"):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f"SELECT * FROM {table} WHERE vehicle_id = ? ORDER BY {order_by}",
        (vehicle_id,),
    ).fetchall()
    conn.close()
    return rows


# ---------- Podesavanja (koristi tema aplikacije - NE MENJATI) ----------

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
    if cena_rsd is None:
        return 0
    if get_valuta() == "EUR":
        return cena_rsd / get_kurs()
    return cena_rsd


def valuta_oznaka():
    return "EUR" if get_valuta() == "EUR" else "RSD"


# ---------- Pregled troskova po periodu (nedelja / mesec / godina) ----------

def _parsiraj_datum(tekst):
    """Datumi se cuvaju kao 'DD.MM.GGGG'. Vraca datetime ili None ako
    tekst ne moze da se parsira (prazno, pogresan format, itd.)."""
    if not tekst:
        return None
    try:
        return datetime.strptime(tekst.strip(), "%d.%m.%Y")
    except ValueError:
        return None


def _u_periodu(datum, od, do):
    if datum is None:
        return False
    return od <= datum <= do


def troskovi_pregled(vehicle_id, od, do):
    """
    Vraca dict sa zbirom po kategorijama za dato vozilo, za period
    [od, do] (datetime objekti, ukljucujuci oba kraja):
    {'gorivo': iznos_rsd, 'servisi': iznos_rsd, 'osiguranje': iznos_rsd,
     'troskovi': iznos_rsd, 'ukupno': iznos_rsd}
    Sve vrednosti su u RSD (osnovna valuta) - konverzija za prikaz se
    radi posle, preko rsd_u_prikaz().
    """
    zbir = {"gorivo": 0.0, "servisi": 0.0, "osiguranje": 0.0, "troskovi": 0.0}

    for red in get_by_vehicle("gorivo", vehicle_id):
        if _u_periodu(_parsiraj_datum(red["datum"]), od, do):
            zbir["gorivo"] += red["ukupna_cena"] or 0

    for red in get_by_vehicle("servisi", vehicle_id):
        if _u_periodu(_parsiraj_datum(red["datum"]), od, do):
            zbir["servisi"] += red["ukupna_cena"] or 0

    for red in get_by_vehicle("osiguranje", vehicle_id):
        if _u_periodu(_parsiraj_datum(red["datum"]), od, do):
            zbir["osiguranje"] += red["cena"] or 0

    for red in get_by_vehicle("troskovi", vehicle_id):
        if _u_periodu(_parsiraj_datum(red["datum"]), od, do):
            zbir["troskovi"] += red["iznos"] or 0

    zbir["ukupno"] = sum(zbir.values())
    return zbir

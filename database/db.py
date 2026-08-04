"""
Database modul - SQLite konekcija i upiti za MojAuto aplikaciju.

Tabele:
- vozila, gorivo, servisi, ulje, filteri, gume, registracija,
  osiguranje, akumulator, kvarovi, troskovi, dokumenti, podsetnici
- podesavanja (kljuc, vrednost) - koristi je tema aplikacije, NE DIRATI
"""
import sqlite3
import os

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
            napomena TEXT
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

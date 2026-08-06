"""
pdf_report.py

Generisanje kompletnog PDF izvestaja o jednom vozilu - svi podaci iz
svih kategorija (gorivo, servisi, troskovi, gume, registracija,
osiguranje, akumulator, kvarovi, dokumenta, podsetnici).

Napomena o valuti: svaka novcana stavka ima svoju sacuvanu valutu
(RSD ili EUR) - PDF prikazuje tacno tu vrednost, bez konverzije.
"""
import os
from datetime import datetime

from fpdf import FPDF

from database import db


SEKCIJE = [
    ("gorivo", "Gorivo", [
        ("datum", "Datum"), ("kilometraza", "Kilometraza"),
        ("litara", "Litara"), ("cena_po_litru", "Cena/L"),
        ("ukupna_cena", "Ukupno"), ("pumpa", "Pumpa"), ("grad", "Grad"),
    ]),
    ("servisi", "Servisi", [
        ("datum", "Datum"), ("tip", "Tip"), ("naziv", "Naziv"),
        ("kilometraza", "Kilometraza"), ("cena_delova", "Delovi"),
        ("cena_rada", "Rad"), ("ukupna_cena", "Ukupno"),
    ]),
    ("troskovi", "Troskovi", [
        ("datum", "Datum"), ("vrsta", "Vrsta"), ("iznos", "Iznos"),
        ("napomena", "Napomena"),
    ]),
    ("gume", "Gume", [
        ("sezona", "Sezona"), ("marka", "Marka"), ("model", "Model"),
        ("dimenzija", "Dimenzija"), ("dot", "DOT"), ("cena", "Cena"),
        ("datum_kupovine", "Datum kupovine"),
    ]),
    ("registracija", "Registracija", [
        ("datum_registracije", "Datum"), ("istek", "Istek"),
        ("cena", "Cena"), ("tehnicki_pregled", "Tehnicki pregled"),
    ]),
    ("osiguranje", "Osiguranje", [
        ("vrsta", "Vrsta"), ("cena", "Cena"), ("datum", "Datum"), ("istek", "Istek"),
    ]),
    ("akumulator", "Akumulator", [
        ("marka", "Marka"), ("model", "Model"), ("kapacitet", "Kapacitet"),
        ("datum_kupovine", "Datum kupovine"), ("cena", "Cena"), ("garancija", "Garancija"),
    ]),
    ("kvarovi", "Kvarovi", [
        ("datum", "Datum"), ("kilometraza", "Kilometraza"), ("opis", "Opis"),
        ("ukupna_cena", "Ukupno"),
    ]),
    ("dokumenti", "Dokumenta", [
        ("tip", "Tip"), ("naziv", "Naziv"), ("datum_dodavanja", "Datum dodavanja"),
    ]),
    ("podsetnici", "Podsetnici", [
        ("tip", "Tip"), ("naslov", "Naslov"), ("datum_isteka", "Istek"),
        ("kilometraza_isteka", "Kilometraza isteka"),
    ]),
]

NOVCANA_POLJA = {"cena_po_litru", "ukupna_cena", "cena_delova", "cena_rada",
                 "iznos", "cena"}

ZAMENA_SLOVA = str.maketrans({
    "č": "c", "ć": "c", "đ": "dj",
    "Č": "C", "Ć": "C", "Đ": "Dj",
})


def _ascii_bezbedno(tekst):
    """Font koji koristimo (Helvetica) ne podrzava c/c/dj - zamenjuje
    ih ASCII ekvivalentima da PDF ne bi pukao. s i z ostaju (font ih
    podrzava)."""
    if tekst is None:
        return ""
    return str(tekst).translate(ZAMENA_SLOVA)


def _formatiraj_vrednost(kljuc, vrednost, valuta=None):
    if vrednost is None:
        return "-"
    if kljuc in NOVCANA_POLJA:
        try:
            return f"{float(vrednost):.2f} {valuta or 'RSD'}"
        except (TypeError, ValueError):
            return _ascii_bezbedno(vrednost)
    return _ascii_bezbedno(vrednost)


def _izlazna_putanja(naziv_fajla):
    try:
        from android.storage import primary_external_storage_path
        downloads = os.path.join(primary_external_storage_path(), "Download")
    except ImportError:
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(downloads, exist_ok=True)
    return os.path.join(downloads, naziv_fajla)


def generisi_pdf_izvestaj(vozilo):
    """
    vozilo: sqlite3.Row iz tabele 'vozila'.
    Vraca putanju do sacuvanog PDF fajla.
    """
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "MojAuto - Izvestaj o vozilu", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generisano: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _ascii_bezbedno(f"{vozilo['marka']} {vozilo['model']} ({vozilo['godina'] or '-'})"), ln=True)

    vozilo_valuta = vozilo["valuta"] if "valuta" in vozilo.keys() else None

    pdf.set_font("Helvetica", "", 11)
    osnovni_podaci = [
        ("Registracija", vozilo["registracija"], False),
        ("VIN", vozilo["vin"], False),
        ("Broj sasije", vozilo["broj_sasije"], False),
        ("Broj motora", vozilo["broj_motora"], False),
        ("Gorivo", vozilo["gorivo"], False),
        ("Zapremina", vozilo["zapremina"], False),
        ("Snaga (KS)", vozilo["snaga"], False),
        ("Menjac", vozilo["menjac"], False),
        ("Boja", vozilo["boja"], False),
        ("Broj vrata", vozilo["broj_vrata"] if "broj_vrata" in vozilo.keys() else None, False),
        ("Kilometraza", vozilo["kilometraza"], False),
        ("Kupovna cena", vozilo["kupovna_cena"], True),
    ]
    for naziv, vrednost, je_novac in osnovni_podaci:
        if je_novac:
            vrednost_tekst = _formatiraj_vrednost("cena", vrednost, vozilo_valuta) if vrednost not in (None, "") else "-"
        else:
            vrednost_tekst = _ascii_bezbedno(vrednost) if vrednost not in (None, "") else "-"
        pdf.cell(0, 7, f"{naziv}: {vrednost_tekst}", ln=True)

    pdf.ln(6)

    for tabela, naslov, kolone in SEKCIJE:
        zapisi = db.get_by_vehicle(tabela, vozilo["id"], order_by="id DESC")

        pdf.set_font("Helvetica", "B", 13)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 9, naslov, ln=True, fill=True)

        if not zapisi:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, "Nema zapisa.", ln=True)
            pdf.ln(3)
            continue

        pdf.set_font("Helvetica", "", 9)
        for red in zapisi:
            red_valuta = red["valuta"] if "valuta" in red.keys() else None
            linija = " | ".join(
                f"{label}: {_formatiraj_vrednost(kljuc, red[kljuc], red_valuta)}"
                for kljuc, label in kolone
            )
            pdf.multi_cell(0, 6, linija)
            pdf.ln(1)

        pdf.ln(3)

    naziv_fajla = f"MojAuto_{vozilo['marka']}_{vozilo['model']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    naziv_fajla = _ascii_bezbedno(naziv_fajla).replace(" ", "_")
    putanja = _izlazna_putanja(naziv_fajla)
    pdf.output(putanja)
    return putanja

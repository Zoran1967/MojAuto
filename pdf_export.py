"""
Generisanje PDF racuna (jedan zatvoreni racun iz istorije kupovina).

Koristi fpdf2 - cist Python paket bez C ekstenzija. Namerno se NE koristi
reportlab, jer njegov "recept" u python-for-android/Buildozer alatu ima
poznat, dugogodisnji i nezavrsen problem koji na Androidu izbacuje
"No module named 'reportlab'" iako je paket naveden u requirements.
fpdf2 nema taj problem jer se instalira kao obican pure-python paket.

PDF se cuva u javni Downloads folder na telefonu (ne zahteva posebne
Android dozvole za deljenje/FileProvider) - korisnik ga otvara iz bilo
kog PDF citaca (Google Drive, Adobe i sl.) i stampa odatle direktno,
koristeci "Stampaj" dugme koje vec postoji u tim aplikacijama.

Napomena: tekst u PDF-u je namerno na neutralnom/latinicnom formatu
(bez posebnih Unicode fontova) da bi radio pouzdano na svim uredjajima
bez dodatnog TTF fonta u APK-u - nazivi proizvoda i prodavnica koje
korisnik unosi su vec u tom formatu (konvencija cele aplikacije).
"""
import os
from datetime import datetime

from fpdf import FPDF
from kivy.utils import platform


def _downloads_folder():
    """Putanja do javnog Downloads foldera. Na Androidu koristi
    primarni eksterni storage; na desktopu (test) pravi lokalni
    'downloads' folder pored aplikacije."""
    if platform == "android":
        try:
            from android.storage import primary_external_storage_path
            folder = os.path.join(primary_external_storage_path(), "Download")
        except Exception:
            folder = os.path.expanduser("~/storage/downloads")
    else:
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

    os.makedirs(folder, exist_ok=True)
    return folder


def _bezbedno_ime(tekst):
    """Uklanja znakove koji ne smeju biti u imenu fajla."""
    dozvoljeno = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_- "
    return "".join(c if c in dozvoljeno else "_" for c in str(tekst)).strip() or "racun"


def _kao_broj(vrednost):
    """
    Pokusava da pretvori vrednost u float (podrzava i zarez kao decimalni
    separator, npr. '125,50'). Ako ne uspe, vraca None.
    """
    if isinstance(vrednost, (int, float)):
        return float(vrednost)
    if isinstance(vrednost, str):
        ocisceno = vrednost.strip().replace(" ", "")
        if "," in ocisceno and "." not in ocisceno:
            ocisceno = ocisceno.replace(",", ".")
        try:
            return float(ocisceno)
        except ValueError:
            return None
    return None


def _format_broj(vrednost, decimale=2):
    """
    Bezbedno formatira vrednost sa fiksnim brojem decimala.
    Radi bez obzira da li je vrednost broj ili vec formatiran string -
    ako ne moze da se konvertuje u broj, vraca tekst vrednosti onakav
    kakav je prosledjen.
    """
    broj = _kao_broj(vrednost)
    if broj is None:
        return str(vrednost)
    return f"{broj:.{decimale}f}"


def _format_kolicina(vrednost):
    """
    Isto kao _format_broj, ali za kolicinu koristi format bez nepotrebnih
    nula (npr. 2 umesto 2.00), uz istu zastitu od stringova koji ne mogu
    da se konvertuju u broj.
    """
    broj = _kao_broj(vrednost)
    if broj is None:
        return str(vrednost)
    if broj == int(broj):
        return str(int(broj))
    return f"{broj:g}"


# Sirine kolona u mm - moraju se poklapati sa brojem kolona u zaglavlju
_KOLONE_SIRINE = [70, 22, 38, 38]
_KOLONE_PORAVNANJE = ["L", "R", "R", "R"]


def _red_tabele(pdf, vrednosti, popuna=False, podebljano=False, visina=8):
    if podebljano:
        pdf.set_font("Helvetica", "B", 10)
    else:
        pdf.set_font("Helvetica", "", 10)
    for tekst, sirina, poravnanje in zip(vrednosti, _KOLONE_SIRINE, _KOLONE_PORAVNANJE):
        pdf.cell(sirina, visina, tekst, border=1, align=poravnanje, fill=popuna)
    pdf.ln(visina)


def generisi_racun_pdf(prodavnica_naziv, datum, stavke, ukupno_prikaz, valuta_oznaka):
    """
    Pravi PDF fajl za jedan racun i vraca putanju do njega.

    stavke: lista (naziv, kolicina, cena_po_jedinici_prikaz, total_prikaz)

    Napomena: kolicina/cena/total i ukupno_prikaz mogu biti brojevi
    (int/float) ili vec formatirani stringovi (npr. '125,50') - funkcija
    bezbedno radi sa oba slucaja.
    """
    folder = _downloads_folder()
    vremenska_oznaka = datetime.now().strftime("%Y%m%d_%H%M%S")
    ime_fajla = f"Racun_{_bezbedno_ime(prodavnica_naziv)}_{vremenska_oznaka}.pdf"
    putanja = os.path.join(folder, ime_fajla)

    pdf = FPDF(format="A4")
    pdf.set_margins(16, 18, 16)
    pdf.add_page()

    # Naslov (naziv prodavnice)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, str(prodavnica_naziv), ln=1)

    # Podnaslov (datum)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f"Datum kupovine: {datum}", ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Zaglavlje tabele
    pdf.set_fill_color(27, 31, 42)
    pdf.set_text_color(255, 255, 255)
    _red_tabele(
        pdf,
        ["Proizvod", "Kol.", f"Cena/j. ({valuta_oznaka})", f"Ukupno ({valuta_oznaka})"],
        popuna=True, podebljano=True,
    )
    pdf.set_text_color(0, 0, 0)

    # Stavke racuna
    for naziv, kolicina, cena, total in stavke:
        _red_tabele(pdf, [
            str(naziv),
            _format_kolicina(kolicina),
            _format_broj(cena),
            _format_broj(total),
        ])

    # Red sa ukupnim iznosom
    _red_tabele(
        pdf,
        ["", "", "UKUPNO:", f"{_format_broj(ukupno_prikaz)} {valuta_oznaka}"],
        podebljano=True,
    )

    # Footer
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Napravljeno u aplikaciji Soping Lista.", ln=1)

    pdf.output(putanja)
    return putanja

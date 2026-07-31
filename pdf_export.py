"""
Generisanje PDF racuna (jedan zatvoreni racun iz istorije kupovina).

Koristi reportlab (cist Python, radi i na Androidu preko Buildozer-a
ako se doda u requirements u buildozer.spec).

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

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
    return "".join(c if c in dozvoljeno else "_" for c in tekst).strip() or "racun"


def generisi_racun_pdf(prodavnica_naziv, datum, stavke, ukupno_prikaz, valuta_oznaka):
    """
    Pravi PDF fajl za jedan racun i vraca putanju do njega.

    stavke: lista (naziv, kolicina, cena_po_jedinici_prikaz, total_prikaz)
    """
    folder = _downloads_folder()
    vremenska_oznaka = datetime.now().strftime("%Y%m%d_%H%M%S")
    ime_fajla = f"Racun_{_bezbedno_ime(prodavnica_naziv)}_{vremenska_oznaka}.pdf"
    putanja = os.path.join(folder, ime_fajla)

    stilovi = getSampleStyleSheet()
    naslov_stil = ParagraphStyle(
        "Naslov", parent=stilovi["Heading1"], fontSize=18, spaceAfter=4,
    )
    podnaslov_stil = ParagraphStyle(
        "Podnaslov", parent=stilovi["Normal"], fontSize=11, textColor=colors.grey,
        spaceAfter=14,
    )

    doc = SimpleDocTemplate(
        putanja, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm,
    )

    elementi = []
    elementi.append(Paragraph(prodavnica_naziv, naslov_stil))
    elementi.append(Paragraph(f"Datum kupovine: {datum}", podnaslov_stil))

    podaci = [["Proizvod", "Kol.", f"Cena/j. ({valuta_oznaka})", f"Ukupno ({valuta_oznaka})"]]
    for naziv, kolicina, cena, total in stavke:
        podaci.append([
            naziv,
            f"{kolicina:g}",
            f"{cena:.2f}",
            f"{total:.2f}",
        ])
    podaci.append(["", "", "UKUPNO:", f"{ukupno_prikaz:.2f} {valuta_oznaka}"])

    tabela = Table(podaci, colWidths=[70 * mm, 22 * mm, 38 * mm, 38 * mm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b1f2a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.4, colors.grey),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementi.append(tabela)
    elementi.append(Spacer(1, 10 * mm))
    elementi.append(Paragraph(
        "Napravljeno u aplikaciji Soping Lista.",
        ParagraphStyle("Footer", parent=stilovi["Normal"], fontSize=8, textColor=colors.grey),
    ))

    doc.build(elementi)
    return putanja

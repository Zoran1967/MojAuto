"""
ocr_racun.py

Cita racun za gorivo sa slike koriscenjem besplatnog OCR.space API-ja i
pokusava da izvuce naziv pumpe, litre, cenu po litru i ukupnu cenu.
Koristi samo standardnu Python biblioteku (urllib) - nema dodatnih
paketa da se ne bi ponovila prica sa fpdf2/fonttools arhitekturom.
Prepoznavanje je heuristicko (racuni se razlikuju po formatu) - zato
se rezultat uvek prikazuje korisniku da potvrdi/ispravi pre cuvanja.
"""
import re
import json
import ssl
import uuid
import mimetypes
import urllib.request

OCR_API_URL = "https://api.ocr.space/parse/image"

_SSL_KONTEKST = ssl._create_unverified_context()


def _posalji_zahtev(putanja_slike, api_key):
    putanja_slike = str(putanja_slike)
    boundary = uuid.uuid4().hex
    with open(putanja_slike, "rb") as f:
        slika_bajtovi = f.read()

    naziv_fajla = putanja_slike.rsplit("/", 1)[-1]
    content_type = mimetypes.guess_type(naziv_fajla)[0] or "image/jpeg"

    delovi = []

    def dodaj_polje(ime, vrednost):
        delovi.append(f"--{boundary}\r\n".encode())
        delovi.append(f'Content-Disposition: form-data; name="{ime}"\r\n\r\n'.encode())
        delovi.append(f"{vrednost}\r\n".encode())

    dodaj_polje("apikey", api_key)
    dodaj_polje("language", "eng")
    dodaj_polje("OCREngine", "2")
    dodaj_polje("scale", "true")

    delovi.append(f"--{boundary}\r\n".encode())
    delovi.append(f'Content-Disposition: form-data; name="file"; filename="{naziv_fajla}"\r\n'.encode())
    delovi.append(f"Content-Type: {content_type}\r\n\r\n".encode())
    delovi.append(slika_bajtovi)
    delovi.append(b"\r\n")
    delovi.append(f"--{boundary}--\r\n".encode())

    telo = b"".join(delovi)

    zahtev = urllib.request.Request(
        OCR_API_URL, data=telo, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(zahtev, timeout=30, context=_SSL_KONTEKST) as odgovor:
        return json.loads(odgovor.read().decode("utf-8"))


def ocitaj_racun(putanja_slike, api_key):
    """
    Vraca dict: {"pumpa", "litara", "cena_po_litru", "ukupna_cena", "sirovi_tekst"}.
    Bilo koja vrednost moze biti None ako nije prepoznata.
    Baca Exception sa opisom greske ako OCR servis ne uspe da obradi sliku.
    """
    rezultat = _posalji_zahtev(putanja_slike, api_key)

    if rezultat.get("IsErroredOnProcessing"):
        poruka = rezultat.get("ErrorMessage") or ["Nepoznata OCR greska"]
        if isinstance(poruka, list):
            poruka = poruka[0]
        raise Exception(poruka)

    parsed_lista = rezultat.get("ParsedResults") or []
    if not parsed_lista:
        raise Exception("OCR nije vratio nikakav tekst.")

    tekst = parsed_lista[0].get("ParsedText", "")

    return {
        "pumpa": _nadji_pumpu(tekst),
        "litara": _nadji_broj(tekst, [
            r"(\d+[.,]\d{2,3})\s*[lL](?:it)?\b",
            r"litar[a]?\D{0,10}(\d+[.,]\d+)",
        ]),
        "cena_po_litru": _nadji_broj(tekst, [
            r"cena.{0,15}?(\d+[.,]\d+)",
            r"/\s*[lL]\D{0,5}(\d+[.,]\d+)",
            r"price.{0,10}?/.{0,5}?liter.{0,10}?(\d+[.,]\d+)",
        ]),
        "ukupna_cena": _nadji_ukupno(tekst),
        "sirovi_tekst": tekst,
    }


def _nadji_broj(tekst, obrasci):
    for obrazac in obrasci:
        m = re.search(obrazac, tekst, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(",", "."))
            except ValueError:
                continue
    return None


def _nadji_ukupno(tekst):
    for red in tekst.splitlines():
        if re.search(r"ukupno|total|za\s*platiti|iznos", red, re.IGNORECASE):
            m = re.search(r"(\d+[.,]\d{2,3})", red)
            if m:
                try:
                    return float(m.group(1).replace(",", "."))
                except ValueError:
                    continue
    return None


def _nadji_pumpu(tekst):
    for red in tekst.splitlines():
        red = red.strip()
        if len(red) > 3 and not re.search(r"\d{4,}", red):
            return red[:40]
    return None

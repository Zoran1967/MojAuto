"""
ocr_racun.py

Cita racun za gorivo sa slike koriscenjem besplatnog OCR.space API-ja i
pokusava da izvuce naziv pumpe, litre, cenu po litru i ukupnu cenu.
Prepoznavanje je heuristicko (racuni se razlikuju po formatu) - zato
se rezultat uvek prikazuje korisniku da potvrdi/ispravi pre cuvanja.
"""
import re
import requests

OCR_API_URL = "https://api.ocr.space/parse/image"


def ocitaj_racun(putanja_slike, api_key):
    """
    Vraca dict: {"pumpa", "litara", "cena_po_litru", "ukupna_cena", "sirovi_tekst"}.
    Bilo koja vrednost moze biti None ako nije prepoznata.
    Baca Exception sa opisom greske ako OCR servis ne uspe da obradi sliku.
    """
    with open(putanja_slike, "rb") as f:
        odgovor = requests.post(
            OCR_API_URL,
            files={"file": f},
            data={"apikey": api_key, "language": "eng", "OCREngine": 2, "scale": "true"},
            timeout=30,
        )
    rezultat = odgovor.json()

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

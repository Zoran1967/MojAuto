"""
translations.py

Centralni recnik prevoda za MojAuto aplikaciju.
Jezici: sr (srpski), en (engleski), de (nemacki), sk (slovacki),
uk (ukrajinski), it (italijanski), fr (francuski), bg (bugarski).

Postepeno se dopunjuje - trenutno sadrzi samo tekstove pocetnog ekrana.
"""

PREVODI = {
    "home_title": {
        "sr": "MojAuto",
        "en": "MojAuto",
        "de": "MojAuto",
        "sk": "MojAuto",
        "uk": "MojAuto",
        "it": "MojAuto",
        "fr": "MojAuto",
        "bg": "MojAuto",
    },
    "home_vozila": {
        "sr": "Vozila",
        "en": "Vehicles",
        "de": "Fahrzeuge",
        "sk": "Vozidla",
        "uk": "Транспорт",
        "it": "Veicoli",
        "fr": "Vehicules",
        "bg": "Превозни средства",
    },
    "home_zapisi": {
        "sr": "Zapisi",
        "en": "Records",
        "de": "Eintrage",
        "sk": "Zaznamy",
        "uk": "Записи",
        "it": "Registri",
        "fr": "Enregistrements",
        "bg": "Записи",
    },
    "home_istorija": {
        "sr": "Istorija",
        "en": "History",
        "de": "Verlauf",
        "sk": "Historia",
        "uk": "Історія",
        "it": "Cronologia",
        "fr": "Historique",
        "bg": "История",
    },
    "home_podesavanja": {
        "sr": "Podesavanja",
        "en": "Settings",
        "de": "Einstellungen",
        "sk": "Nastavenia",
        "uk": "Налаштування",
        "it": "Impostazioni",
        "fr": "Parametres",
        "bg": "Настройки",
    },
    "home_language": {
        "sr": "JEZIK",
        "en": "LANGUAGE",
        "de": "SPRACHE",
        "sk": "JAZYK",
        "uk": "МОВА",
        "it": "LINGUA",
        "fr": "LANGUE",
        "bg": "ЕЗИК",
    },
}


def prevedi(kljuc, jezik="sr"):
    """Vraca preveden tekst za dati kljuc i jezik. Ako kljuc ili jezik
    ne postoje, vraca srpski tekst (ili sam kljuc ako ni to ne postoji) -
    da aplikacija nikad ne ostane bez teksta na ekranu."""
    stavka = PREVODI.get(kljuc)
    if stavka is None:
        return kljuc
    return stavka.get(jezik, stavka.get("sr", kljuc))

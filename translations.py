"""
Prevodi tekstova aplikacije. Naziv aplikacije (Shopping List) ostaje
uvek na engleskom, bez obzira na izabrani jezik - prevode se samo
tekstovi unutar ekrana.
"""

PREVODI = {
    "sr": {
        "home_new_list": "Nova lista\nza kupovinu",
        "home_history": "Istorija\nkupovina",
        "home_database": "Baza proizvoda\ni prodavnica",
        "home_settings": "Podesavanja",
        "home_language_label": "Jezik",
    },
    "en": {
        "home_new_list": "New list\nfor shopping",
        "home_history": "Shopping\nhistory",
        "home_database": "Product\ndatabase",
        "home_settings": "Settings",
        "home_language_label": "Language",
    },
    "sk": {
        "home_new_list": "Novy zoznam\nna nakup",
        "home_history": "Historia\nnakupov",
        "home_database": "Databaza\nproduktov",
        "home_settings": "Nastavenia",
        "home_language_label": "Jazyk",
    },
    "uk": {
        "home_new_list": "Новий список\nдля покупок",
        "home_history": "Історія\nпокупок",
        "home_database": "База\nтоварів",
        "home_settings": "Налаштування",
        "home_language_label": "Мова",
    },
}


def prevedi(kljuc, jezik):
    """Vraca prevod za dati kljuc i jezik. Ako ne postoji, vraca srpski."""
    return PREVODI.get(jezik, PREVODI["sr"]).get(kljuc, PREVODI["sr"].get(kljuc, kljuc))

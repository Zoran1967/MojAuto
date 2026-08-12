"""
translations.py

Centralni recnik prevoda za MojAuto aplikaciju.
Jezici: sr (srpski), en (engleski), de (nemacki), sk (slovacki),
uk (ukrajinski), it (italijanski), fr (francuski), bg (bugarski).

Sadrzi pocetni ekran, ekran Vozila, ekran Zapisi, ekran Istorija
i ekran Podesavanja.
"""

PREVODI = {
    # ---------- Pocetni ekran ----------
    "home_title": {
        "sr": "MojAuto", "en": "MojAuto", "de": "MojAuto", "sk": "MojAuto",
        "uk": "MojAuto", "it": "MojAuto", "fr": "MojAuto", "bg": "MojAuto",
    },
    "home_vozila": {
        "sr": "Vozila", "en": "Vehicles", "de": "Fahrzeuge", "sk": "Vozidla",
        "uk": "Транспорт", "it": "Veicoli", "fr": "Vehicules", "bg": "Превозни средства",
    },
    "home_zapisi": {
        "sr": "Zapisi", "en": "Records", "de": "Eintrage", "sk": "Zaznamy",
        "uk": "Записи", "it": "Registri", "fr": "Enregistrements", "bg": "Записи",
    },
    "home_istorija": {
        "sr": "Istorija", "en": "History", "de": "Verlauf", "sk": "Historia",
        "uk": "Історія", "it": "Cronologia", "fr": "Historique", "bg": "История",
    },
    "home_podesavanja": {
        "sr": "Podesavanja", "en": "Settings", "de": "Einstellungen", "sk": "Nastavenia",
        "uk": "Налаштування", "it": "Impostazioni", "fr": "Parametres", "bg": "Настройки",
    },
    "home_language": {
        "sr": "JEZIK", "en": "LANGUAGE", "de": "SPRACHE", "sk": "JAZYK",
        "uk": "МОВА", "it": "LINGUA", "fr": "LANGUE", "bg": "ЕЗИК",
    },

    # ---------- Ekran Vozila ----------
    "vozila_naslov": {
        "sr": "Vozila", "en": "Vehicles", "de": "Fahrzeuge", "sk": "Vozidla",
        "uk": "Транспорт", "it": "Veicoli", "fr": "Vehicules", "bg": "Превозни средства",
    },
    "vozila_dodaj_btn": {
        "sr": "+ Dodaj vozilo", "en": "+ Add vehicle", "de": "+ Fahrzeug hinzufugen",
        "sk": "+ Pridat vozidlo", "uk": "+ Додати транспорт", "it": "+ Aggiungi veicolo",
        "fr": "+ Ajouter un vehicule", "bg": "+ Добави превозно средство",
    },
    "vozila_ukupno": {
        "sr": "UKUPNO VOZILA:", "en": "TOTAL VEHICLES:", "de": "FAHRZEUGE GESAMT:",
        "sk": "CELKOM VOZIDIEL:", "uk": "ВСЬОГО ТРАНСПОРТУ:", "it": "TOTALE VEICOLI:",
        "fr": "TOTAL VEHICULES:", "bg": "ОБЩО ПРЕВОЗНИ СРЕДСТВА:",
    },
    "vozila_nema": {
        "sr": "Nema dodatih vozila.", "en": "No vehicles added.", "de": "Keine Fahrzeuge hinzugefugt.",
        "sk": "Ziadne vozidla neboli pridane.", "uk": "Немає доданих транспортних засобів.",
        "it": "Nessun veicolo aggiunto.", "fr": "Aucun vehicule ajoute.",
        "bg": "Няма добавени превозни средства.",
    },
    "vozila_izmeni_btn": {
        "sr": "Izmeni / Obrisi", "en": "Edit / Delete", "de": "Bearbeiten / Loschen",
        "sk": "Upravit / Vymazat", "uk": "Редагувати / Видалити", "it": "Modifica / Elimina",
        "fr": "Modifier / Supprimer", "bg": "Редактирай / Изтрий",
    },
    "vozila_dodaj_naslov": {
        "sr": "Dodaj vozilo", "en": "Add vehicle", "de": "Fahrzeug hinzufugen",
        "sk": "Pridat vozidlo", "uk": "Додати транспорт", "it": "Aggiungi veicolo",
        "fr": "Ajouter un vehicule", "bg": "Добави превозно средство",
    },
    "vozila_izmeni_naslov": {
        "sr": "Izmeni vozilo", "en": "Edit vehicle", "de": "Fahrzeug bearbeiten",
        "sk": "Upravit vozidlo", "uk": "Редагувати транспорт", "it": "Modifica veicolo",
        "fr": "Modifier le vehicule", "bg": "Редактирай превозно средство",
    },
    "vozila_obrisi_btn": {
        "sr": "Obrisi vozilo", "en": "Delete vehicle", "de": "Fahrzeug loschen",
        "sk": "Vymazat vozidlo", "uk": "Видалити транспорт", "it": "Elimina veicolo",
        "fr": "Supprimer le vehicule", "bg": "Изтрий превозно средство",
    },
    "vozila_potvrdi_brisanje": {
        "sr": "Potvrdi brisanje", "en": "Confirm delete", "de": "Loschen bestatigen",
        "sk": "Potvrdit vymazanie", "uk": "Підтвердити видалення", "it": "Conferma eliminazione",
        "fr": "Confirmer la suppression", "bg": "Потвърди изтриването",
    },
    "vozila_sacuvaj": {
        "sr": "Sacuvaj", "en": "Save", "de": "Speichern", "sk": "Ulozit",
        "uk": "Зберегти", "it": "Salva", "fr": "Enregistrer", "bg": "Запази",
    },
    "vozila_otkazi": {
        "sr": "Otkazi", "en": "Cancel", "de": "Abbrechen", "sk": "Zrusit",
        "uk": "Скасувати", "it": "Annulla", "fr": "Annuler", "bg": "Отказ",
    },
    "vozila_greska_obavezno": {
        "sr": "Marka i model su obavezni.", "en": "Make and model are required.",
        "de": "Marke und Modell sind erforderlich.", "sk": "Znacka a model su povinne.",
        "uk": "Марка та модель обов'язкові.", "it": "Marca e modello sono obbligatori.",
        "fr": "La marque et le modele sont obligatoires.", "bg": "Марката и моделът са задължителни.",
    },

    # ---------- Polja forme vozila ----------
    "polje_marka": {
        "sr": "Marka", "en": "Make", "de": "Marke", "sk": "Znacka",
        "uk": "Марка", "it": "Marca", "fr": "Marque", "bg": "Марка",
    },
    "polje_model": {
        "sr": "Model", "en": "Model", "de": "Modell", "sk": "Model",
        "uk": "Модель", "it": "Modello", "fr": "Modele", "bg": "Модел",
    },
    "polje_godina": {
        "sr": "Godina", "en": "Year", "de": "Baujahr", "sk": "Rok",
        "uk": "Рік", "it": "Anno", "fr": "Annee", "bg": "Година",
    },
    "polje_registracija": {
        "sr": "Registracija", "en": "License plate", "de": "Kennzeichen", "sk": "Evidencne cislo",
        "uk": "Реєстрація", "it": "Targa", "fr": "Immatriculation", "bg": "Регистрация",
    },
    "polje_vin": {
        "sr": "VIN", "en": "VIN", "de": "FIN", "sk": "VIN",
        "uk": "VIN", "it": "Telaio", "fr": "VIN", "bg": "VIN",
    },
    "polje_broj_sasije": {
        "sr": "Broj sasije", "en": "Chassis number", "de": "Fahrgestellnummer",
        "sk": "Cislo podvozku", "uk": "Номер шасі", "it": "Numero telaio",
        "fr": "Numero de chassis", "bg": "Номер на шаси",
    },
    "polje_broj_motora": {
        "sr": "Broj motora", "en": "Engine number", "de": "Motornummer", "sk": "Cislo motora",
        "uk": "Номер двигуна", "it": "Numero motore", "fr": "Numero de moteur", "bg": "Номер на двигател",
    },
    "polje_gorivo": {
        "sr": "Gorivo", "en": "Fuel", "de": "Kraftstoff", "sk": "Palivo",
        "uk": "Паливо", "it": "Carburante", "fr": "Carburant", "bg": "Гориво",
    },
    "polje_zapremina": {
        "sr": "Zapremina (L)", "en": "Engine size (L)", "de": "Hubraum (L)", "sk": "Objem (L)",
        "uk": "Обʼєм (Л)", "it": "Cilindrata (L)", "fr": "Cylindree (L)", "bg": "Обем (Л)",
    },
    "polje_snaga": {
        "sr": "Snaga (KS)", "en": "Power (HP)", "de": "Leistung (PS)", "sk": "Vykon (k)",
        "uk": "Потужність (к.с.)", "it": "Potenza (CV)", "fr": "Puissance (ch)", "bg": "Мощност (к.с.)",
    },
    "polje_menjac": {
        "sr": "Menjac", "en": "Transmission", "de": "Getriebe", "sk": "Prevodovka",
        "uk": "Коробка передач", "it": "Cambio", "fr": "Boite de vitesses", "bg": "Скоростна кутия",
    },
    "polje_boja": {
        "sr": "Boja", "en": "Color", "de": "Farbe", "sk": "Farba",
        "uk": "Колір", "it": "Colore", "fr": "Couleur", "bg": "Цвят",
    },
    "polje_broj_vrata": {
        "sr": "Broj vrata", "en": "Number of doors", "de": "Anzahl der Turen", "sk": "Pocet dveri",
        "uk": "Кількість дверей", "it": "Numero di porte", "fr": "Nombre de portes", "bg": "Брой врати",
    },
    "polje_datum_kupovine": {
        "sr": "Datum kupovine (DD.MM.GGGG)", "en": "Purchase date (DD.MM.YYYY)",
        "de": "Kaufdatum (TT.MM.JJJJ)", "sk": "Datum kupy (DD.MM.RRRR)",
        "uk": "Дата покупки (ДД.ММ.РРРР)", "it": "Data di acquisto (GG.MM.AAAA)",
        "fr": "Date d'achat (JJ.MM.AAAA)", "bg": "Дата на покупка (ДД.ММ.ГГГГ)",
    },
    "polje_kupovna_cena": {
        "sr": "Kupovna cena", "en": "Purchase price", "de": "Kaufpreis", "sk": "Kupna cena",
        "uk": "Ціна покупки", "it": "Prezzo di acquisto", "fr": "Prix d'achat", "bg": "Покупна цена",
    },
    "polje_kilometraza": {
        "sr": "Kilometraza", "en": "Mileage", "de": "Kilometerstand", "sk": "Najazdene km",
        "uk": "Пробіг", "it": "Chilometraggio", "fr": "Kilometrage", "bg": "Пробег",
    },
    "polje_napomena": {
        "sr": "Napomena", "en": "Note", "de": "Notiz", "sk": "Poznamka",
        "uk": "Примітка", "it": "Nota", "fr": "Remarque", "bg": "Забележка",
    },
    "polje_valuta_kupovina": {
        "sr": "Valuta (kupovna cena)", "en": "Currency (purchase price)", "de": "Wahrung (Kaufpreis)",
        "sk": "Mena (kupna cena)", "uk": "Валюта (ціна покупки)", "it": "Valuta (prezzo di acquisto)",
        "fr": "Devise (prix d'achat)", "bg": "Валута (покупна цена)",
    },

    # ---------- Ekran Zapisi: opsti tekstovi ----------
    "zapisi_naslov": {
        "sr": "Zapisi vozila", "en": "Vehicle records", "de": "Fahrzeugeintrage",
        "sk": "Zaznamy vozidla", "uk": "Записи транспорту", "it": "Registri veicolo",
        "fr": "Enregistrements du vehicule", "bg": "Записи за превозното средство",
    },
    "zapisi_nema_vozila": {
        "sr": "Nema dodatih vozila.", "en": "No vehicles added.", "de": "Keine Fahrzeuge hinzugefugt.",
        "sk": "Ziadne vozidla neboli pridane.", "uk": "Немає доданих транспортних засобів.",
        "it": "Nessun veicolo aggiunto.", "fr": "Aucun vehicule ajoute.",
        "bg": "Няма добавени превозни средства.",
    },
    "zapisi_prvo_izaberi": {
        "sr": "Prvo izaberite vozilo iz liste ispod.", "en": "First select a vehicle from the list below.",
        "de": "Wahlen Sie zuerst ein Fahrzeug aus der Liste unten.", "sk": "Najprv vyberte vozidlo zo zoznamu nizsie.",
        "uk": "Спочатку виберіть транспорт зі списку нижче.", "it": "Seleziona prima un veicolo dall'elenco sottostante.",
        "fr": "Selectionnez d'abord un vehicule dans la liste ci-dessous.", "bg": "Първо изберете превозно средство от списъка по-долу.",
    },
    "zapisi_u_redu": {
        "sr": "U redu", "en": "OK", "de": "OK", "sk": "OK",
        "uk": "ОК", "it": "OK", "fr": "OK", "bg": "ОК",
    },
    "zapisi_nema_zapisa": {
        "sr": "Nema zapisa.", "en": "No records.", "de": "Keine Eintrage.", "sk": "Ziadne zaznamy.",
        "uk": "Немає записів.", "it": "Nessun registro.", "fr": "Aucun enregistrement.", "bg": "Няма записи.",
    },
    "zapisi_dodaj_zapis": {
        "sr": "+ Dodaj zapis", "en": "+ Add record", "de": "+ Eintrag hinzufugen", "sk": "+ Pridat zaznam",
        "uk": "+ Додати запис", "it": "+ Aggiungi registro", "fr": "+ Ajouter un enregistrement",
        "bg": "+ Добави запис",
    },
    "zapisi_zatvori": {
        "sr": "Zatvori", "en": "Close", "de": "Schliessen", "sk": "Zatvorit",
        "uk": "Закрити", "it": "Chiudi", "fr": "Fermer", "bg": "Затвори",
    },
    "zapisi_novi_zapis": {
        "sr": "Novi zapis", "en": "New record", "de": "Neuer Eintrag", "sk": "Novy zaznam",
        "uk": "Новий запис", "it": "Nuovo registro", "fr": "Nouvel enregistrement", "bg": "Нов запис",
    },
    "zapisi_izmeni_zapis": {
        "sr": "Izmeni zapis", "en": "Edit record", "de": "Eintrag bearbeiten", "sk": "Upravit zaznam",
        "uk": "Редагувати запис", "it": "Modifica registro", "fr": "Modifier l'enregistrement",
        "bg": "Редактирай запис",
    },
    "zapisi_obrisi_zapis": {
        "sr": "Obrisi zapis", "en": "Delete record", "de": "Eintrag loschen", "sk": "Vymazat zaznam",
        "uk": "Видалити запис", "it": "Elimina registro", "fr": "Supprimer l'enregistrement",
        "bg": "Изтрий запис",
    },
    "zapisi_sacuvaj": {
        "sr": "Sacuvaj", "en": "Save", "de": "Speichern", "sk": "Ulozit",
        "uk": "Зберегти", "it": "Salva", "fr": "Enregistrer", "bg": "Запази",
    },
    "zapisi_otkazi": {
        "sr": "Otkazi", "en": "Cancel", "de": "Abbrechen", "sk": "Zrusit",
        "uk": "Скасувати", "it": "Annulla", "fr": "Annuler", "bg": "Отказ",
    },
    "zapisi_potvrdi_brisanje": {
        "sr": "Potvrdi brisanje", "en": "Confirm delete", "de": "Loschen bestatigen",
        "sk": "Potvrdit vymazanie", "uk": "Підтвердити видалення", "it": "Conferma eliminazione",
        "fr": "Confirmer la suppression", "bg": "Потвърди изтриването",
    },
    "polje_valuta": {
        "sr": "Valuta", "en": "Currency", "de": "Wahrung", "sk": "Mena",
        "uk": "Валюта", "it": "Valuta", "fr": "Devise", "bg": "Валута",
    },

    # ---------- Nazivi kategorija ----------
    "kat_gorivo": {
        "sr": "Gorivo", "en": "Fuel", "de": "Kraftstoff", "sk": "Palivo",
        "uk": "Паливо", "it": "Carburante", "fr": "Carburant", "bg": "Гориво",
    },
    "kat_servisi": {
        "sr": "Servisi", "en": "Services", "de": "Wartungen", "sk": "Servisy",
        "uk": "Сервіси", "it": "Manutenzioni", "fr": "Entretiens", "bg": "Сервизи",
    },
    "kat_troskovi": {
        "sr": "Troskovi", "en": "Expenses", "de": "Ausgaben", "sk": "Naklady",
        "uk": "Витрати", "it": "Spese", "fr": "Depenses", "bg": "Разходи",
    },
    "kat_gume": {
        "sr": "Gume", "en": "Tires", "de": "Reifen", "sk": "Pneumatiky",
        "uk": "Шини", "it": "Pneumatici", "fr": "Pneus", "bg": "Гуми",
    },
    "kat_registracija": {
        "sr": "Registracija", "en": "Registration", "de": "Zulassung", "sk": "Registracia",
        "uk": "Реєстрація", "it": "Immatricolazione", "fr": "Immatriculation", "bg": "Регистрация",
    },
    "kat_osiguranje": {
        "sr": "Osiguranje", "en": "Insurance", "de": "Versicherung", "sk": "Poistenie",
        "uk": "Страхування", "it": "Assicurazione", "fr": "Assurance", "bg": "Застраховка",
    },
    "kat_akumulator": {
        "sr": "Akumulator", "en": "Battery", "de": "Batterie", "sk": "Akumulator",
        "uk": "Акумулятор", "it": "Batteria", "fr": "Batterie", "bg": "Акумулатор",
    },
    "kat_kvarovi": {
        "sr": "Kvarovi", "en": "Faults", "de": "Defekte", "sk": "Poruchy",
        "uk": "Несправності", "it": "Guasti", "fr": "Pannes", "bg": "Повреди",
    },
    "kat_dokumenta": {
        "sr": "Dokumenta", "en": "Documents", "de": "Dokumente", "sk": "Dokumenty",
        "uk": "Документи", "it": "Documenti", "fr": "Documents", "bg": "Документи",
    },
    "kat_podsetnici": {
        "sr": "Podsetnici", "en": "Reminders", "de": "Erinnerungen", "sk": "Pripomienky",
        "uk": "Нагадування", "it": "Promemoria", "fr": "Rappels", "bg": "Напомняния",
    },
    "kat_pdf": {
        "sr": "PDF", "en": "PDF", "de": "PDF", "sk": "PDF",
        "uk": "PDF", "it": "PDF", "fr": "PDF", "bg": "PDF",
    },

    # ---------- Polja: Gorivo ----------
    "polje_datum": {
        "sr": "Datum (DD.MM.GGGG)", "en": "Date (DD.MM.YYYY)", "de": "Datum (TT.MM.JJJJ)",
        "sk": "Datum (DD.MM.RRRR)", "uk": "Дата (ДД.ММ.РРРР)", "it": "Data (GG.MM.AAAA)",
        "fr": "Date (JJ.MM.AAAA)", "bg": "Дата (ДД.ММ.ГГГГ)",
    },
    "polje_litara": {
        "sr": "Litara", "en": "Liters", "de": "Liter", "sk": "Litre",
        "uk": "Літри", "it": "Litri", "fr": "Litres", "bg": "Литри",
    },
    "polje_cena_po_litru": {
        "sr": "Cena po litru", "en": "Price per liter", "de": "Preis pro Liter", "sk": "Cena za liter",
        "uk": "Ціна за літр", "it": "Prezzo al litro", "fr": "Prix au litre", "bg": "Цена на литър",
    },
    "polje_pumpa": {
        "sr": "Pumpa", "en": "Gas station", "de": "Tankstelle", "sk": "Cerpacia stanica",
        "uk": "Заправка", "it": "Stazione di servizio", "fr": "Station-service", "bg": "Бензиностанция",
    },
    "polje_grad": {
        "sr": "Grad", "en": "City", "de": "Stadt", "sk": "Mesto",
        "uk": "Місто", "it": "Citta", "fr": "Ville", "bg": "Град",
    },

    # ---------- Polja: Servisi ----------
    "polje_tip_servisa": {
        "sr": "Tip servisa", "en": "Service type", "de": "Servicetyp", "sk": "Typ servisu",
        "uk": "Тип сервісу", "it": "Tipo di intervento", "fr": "Type d'entretien", "bg": "Тип сервиз",
    },
    "polje_naziv": {
        "sr": "Naziv", "en": "Name", "de": "Bezeichnung", "sk": "Nazov",
        "uk": "Назва", "it": "Nome", "fr": "Nom", "bg": "Наименование",
    },
    "polje_opis": {
        "sr": "Opis", "en": "Description", "de": "Beschreibung", "sk": "Popis",
        "uk": "Опис", "it": "Descrizione", "fr": "Description", "bg": "Описание",
    },
    "polje_cena_delova": {
        "sr": "Cena delova", "en": "Parts cost", "de": "Teilekosten", "sk": "Cena dielov",
        "uk": "Вартість запчастин", "it": "Costo dei ricambi", "fr": "Cout des pieces", "bg": "Цена на частите",
    },
    "polje_cena_rada": {
        "sr": "Cena rada", "en": "Labor cost", "de": "Arbeitskosten", "sk": "Cena prace",
        "uk": "Вартість роботи", "it": "Costo della manodopera", "fr": "Cout de la main d'oeuvre",
        "bg": "Цена на труда",
    },

    # ---------- Polja: Troskovi ----------
    "polje_vrsta_troska": {
        "sr": "Vrsta troska", "en": "Expense type", "de": "Ausgabenart", "sk": "Druh nakladu",
        "uk": "Тип витрати", "it": "Tipo di spesa", "fr": "Type de depense", "bg": "Вид разход",
    },
    "polje_iznos": {
        "sr": "Iznos", "en": "Amount", "de": "Betrag", "sk": "Suma",
        "uk": "Сума", "it": "Importo", "fr": "Montant", "bg": "Сума",
    },

    # ---------- Polja: Gume ----------
    "polje_sezona": {
        "sr": "Sezona (letnje/zimske)", "en": "Season (summer/winter)", "de": "Saison (Sommer/Winter)",
        "sk": "Sezona (letne/zimne)", "uk": "Сезон (літні/зимові)", "it": "Stagione (estive/invernali)",
        "fr": "Saison (ete/hiver)", "bg": "Сезон (летни/зимни)",
    },
    "polje_dimenzija": {
        "sr": "Dimenzija", "en": "Size", "de": "Grosse", "sk": "Rozmer",
        "uk": "Розмір", "it": "Dimensione", "fr": "Dimension", "bg": "Размер",
    },
    "polje_dot": {
        "sr": "DOT", "en": "DOT", "de": "DOT", "sk": "DOT",
        "uk": "DOT", "it": "DOT", "fr": "DOT", "bg": "DOT",
    },
    "polje_cena": {
        "sr": "Cena", "en": "Price", "de": "Preis", "sk": "Cena",
        "uk": "Ціна", "it": "Prezzo", "fr": "Prix", "bg": "Цена",
    },
    "polje_kilometraza_montaze": {
        "sr": "Kilometraza montaze", "en": "Mileage at install", "de": "Kilometerstand bei Montage",
        "sk": "Najazdene km pri montazi", "uk": "Пробіг при встановленні", "it": "Chilometraggio al montaggio",
        "fr": "Kilometrage au montage", "bg": "Пробег при монтажа",
    },

    # ---------- Polja: Registracija ----------
    "polje_datum_registracije": {
        "sr": "Datum registracije (DD.MM.GGGG)", "en": "Registration date (DD.MM.YYYY)",
        "de": "Zulassungsdatum (TT.MM.JJJJ)", "sk": "Datum registracie (DD.MM.RRRR)",
        "uk": "Дата реєстрації (ДД.ММ.РРРР)", "it": "Data di immatricolazione (GG.MM.AAAA)",
        "fr": "Date d'immatriculation (JJ.MM.AAAA)", "bg": "Дата на регистрация (ДД.ММ.ГГГГ)",
    },
    "polje_istek": {
        "sr": "Istek (DD.MM.GGGG)", "en": "Expiry (DD.MM.YYYY)", "de": "Ablauf (TT.MM.JJJJ)",
        "sk": "Platnost do (DD.MM.RRRR)", "uk": "Термін дії (ДД.ММ.РРРР)", "it": "Scadenza (GG.MM.AAAA)",
        "fr": "Expiration (JJ.MM.AAAA)", "bg": "Изтича на (ДД.ММ.ГГГГ)",
    },
    "polje_tehnicki_pregled": {
        "sr": "Tehnicki pregled", "en": "Technical inspection", "de": "Technische Untersuchung",
        "sk": "Technicka kontrola", "uk": "Технічний огляд", "it": "Revisione tecnica",
        "fr": "Controle technique", "bg": "Технически преглед",
    },

    # ---------- Polja: Osiguranje ----------
    "polje_vrsta_osiguranja": {
        "sr": "Vrsta osiguranja", "en": "Insurance type", "de": "Versicherungsart", "sk": "Druh poistenia",
        "uk": "Тип страхування", "it": "Tipo di assicurazione", "fr": "Type d'assurance", "bg": "Вид застраховка",
    },

    # ---------- Polja: Akumulator ----------
    "polje_kapacitet": {
        "sr": "Kapacitet", "en": "Capacity", "de": "Kapazitat", "sk": "Kapacita",
        "uk": "Ємність", "it": "Capacita", "fr": "Capacite", "bg": "Капацитет",
    },
    "polje_garancija": {
        "sr": "Garancija", "en": "Warranty", "de": "Garantie", "sk": "Zaruka",
        "uk": "Гарантія", "it": "Garanzia", "fr": "Garantie", "bg": "Гаранция",
    },

    # ---------- Polja: Dokumenta ----------
    "polje_tip_dokumenta": {
        "sr": "Tip dokumenta", "en": "Document type", "de": "Dokumenttyp", "sk": "Typ dokumentu",
        "uk": "Тип документа", "it": "Tipo di documento", "fr": "Type de document", "bg": "Тип документ",
    },
    "polje_putanja": {
        "sr": "Putanja/naziv fajla", "en": "File path/name", "de": "Dateipfad/-name", "sk": "Cesta/nazov suboru",
        "uk": "Шлях/назва файлу", "it": "Percorso/nome del file", "fr": "Chemin/nom du fichier",
        "bg": "Път/име на файла",
    },
    "polje_datum_dodavanja": {
        "sr": "Datum dodavanja (DD.MM.GGGG)", "en": "Date added (DD.MM.YYYY)", "de": "Hinzugefugt am (TT.MM.JJJJ)",
        "sk": "Datum pridania (DD.MM.RRRR)", "uk": "Дата додавання (ДД.ММ.РРРР)",
        "it": "Data di aggiunta (GG.MM.AAAA)", "fr": "Date d'ajout (JJ.MM.AAAA)",
        "bg": "Дата на добавяне (ДД.ММ.ГГГГ)",
    },

    # ---------- Polja: Podsetnici ----------
    "polje_tip_podsetnika": {
        "sr": "Tip podsetnika (npr. registracija, servis)", "en": "Reminder type (e.g. registration, service)",
        "de": "Erinnerungstyp (z.B. Zulassung, Service)", "sk": "Typ pripomienky (napr. registracia, servis)",
        "uk": "Тип нагадування (напр. реєстрація, сервіс)", "it": "Tipo di promemoria (es. immatricolazione, tagliando)",
        "fr": "Type de rappel (ex. immatriculation, entretien)", "bg": "Тип напомняне (напр. регистрация, сервиз)",
    },
    "polje_naslov": {
        "sr": "Naslov", "en": "Title", "de": "Titel", "sk": "Nazov",
        "uk": "Заголовок", "it": "Titolo", "fr": "Titre", "bg": "Заглавие",
    },
    "polje_datum_isteka": {
        "sr": "Datum isteka (DD.MM.GGGG)", "en": "Expiry date (DD.MM.YYYY)", "de": "Ablaufdatum (TT.MM.JJJJ)",
        "sk": "Datum platnosti (DD.MM.RRRR)", "uk": "Дата закінчення (ДД.ММ.РРРР)",
        "it": "Data di scadenza (GG.MM.AAAA)", "fr": "Date d'expiration (JJ.MM.AAAA)",
        "bg": "Дата на изтичане (ДД.ММ.ГГГГ)",
    },
    "polje_kilometraza_isteka": {
        "sr": "Kilometraza isteka", "en": "Mileage at expiry", "de": "Kilometerstand bei Ablauf",
        "sk": "Najazdene km pri konci platnosti", "uk": "Пробіг закінчення", "it": "Chilometraggio alla scadenza",
        "fr": "Kilometrage a l'expiration", "bg": "Пробег при изтичане",
    },

    # ---------- Ekran Istorija ----------
    "istorija_naslov": {
        "sr": "Istorija svih zapisa", "en": "History of all records", "de": "Verlauf aller Eintrage",
        "sk": "Historia vsetkych zaznamov", "uk": "Історія всіх записів", "it": "Cronologia di tutti i registri",
        "fr": "Historique de tous les enregistrements", "bg": "История на всички записи",
    },
    "istorija_zapisa_broj": {
        "sr": "zapisa", "en": "records", "de": "Eintrage", "sk": "zaznamov",
        "uk": "записів", "it": "registri", "fr": "enregistrements", "bg": "записа",
    },
    "istorija_svi_zapisi": {
        "sr": "Svi zapisi vozila", "en": "All vehicle records", "de": "Alle Fahrzeugeintrage",
        "sk": "Vsetky zaznamy vozidla", "uk": "Всі записи транспорту", "it": "Tutti i registri del veicolo",
        "fr": "Tous les enregistrements du vehicule", "bg": "Всички записи за превозното средство",
    },
    "istorija_detalji_zapisa": {
        "sr": "Detalji zapisa", "en": "Record details", "de": "Eintragsdetails", "sk": "Detaily zaznamu",
        "uk": "Деталі запису", "it": "Dettagli del registro", "fr": "Details de l'enregistrement",
        "bg": "Детайли на записа",
    },
    "istorija_nazad": {
        "sr": "Nazad", "en": "Back", "de": "Zuruck", "sk": "Spat",
        "uk": "Назад", "it": "Indietro", "fr": "Retour", "bg": "Назад",
    },
    "istorija_naslov_gorivo": {
        "sr": "Gorivo", "en": "Fuel", "de": "Kraftstoff", "sk": "Palivo",
        "uk": "Паливо", "it": "Carburante", "fr": "Carburant", "bg": "Гориво",
    },
    "istorija_naslov_servis": {
        "sr": "Servis", "en": "Service", "de": "Wartung", "sk": "Servis",
        "uk": "Сервіс", "it": "Manutenzione", "fr": "Entretien", "bg": "Сервиз",
    },
    "istorija_naslov_trosak": {
        "sr": "Trosak", "en": "Expense", "de": "Ausgabe", "sk": "Naklad",
        "uk": "Витрата", "it": "Spesa", "fr": "Depense", "bg": "Разход",
    },
    "istorija_naslov_gume": {
        "sr": "Gume", "en": "Tires", "de": "Reifen", "sk": "Pneumatiky",
        "uk": "Шини", "it": "Pneumatici", "fr": "Pneus", "bg": "Гуми",
    },
    "istorija_naslov_registracija": {
        "sr": "Registracija", "en": "Registration", "de": "Zulassung", "sk": "Registracia",
        "uk": "Реєстрація", "it": "Immatricolazione", "fr": "Immatriculation", "bg": "Регистрация",
    },
    "istorija_naslov_osiguranje": {
        "sr": "Osiguranje", "en": "Insurance", "de": "Versicherung", "sk": "Poistenie",
        "uk": "Страхування", "it": "Assicurazione", "fr": "Assurance", "bg": "Застраховка",
    },
    "istorija_naslov_akumulator": {
        "sr": "Akumulator", "en": "Battery", "de": "Batterie", "sk": "Akumulator",
        "uk": "Акумулятор", "it": "Batteria", "fr": "Batterie", "bg": "Акумулатор",
    },
    "istorija_naslov_kvar": {
        "sr": "Kvar", "en": "Fault", "de": "Defekt", "sk": "Porucha",
        "uk": "Несправність", "it": "Guasto", "fr": "Panne", "bg": "Повреда",
    },
    "istorija_naslov_dokument": {
        "sr": "Dokument", "en": "Document", "de": "Dokument", "sk": "Dokument",
        "uk": "Документ", "it": "Documento", "fr": "Document", "bg": "Документ",
    },
    "istorija_naslov_podsetnik": {
        "sr": "Podsetnik", "en": "Reminder", "de": "Erinnerung", "sk": "Pripomienka",
        "uk": "Нагадування", "it": "Promemoria", "fr": "Rappel", "bg": "Напомняне",
    },

    # ---------- Ekran Podesavanja ----------
    "podesavanja_naslov": {
        "sr": "Podesavanja", "en": "Settings", "de": "Einstellungen", "sk": "Nastavenia",
        "uk": "Налаштування", "it": "Impostazioni", "fr": "Parametres", "bg": "Настройки",
    },
    "podesavanja_tema_btn": {
        "sr": "Tema (boja dugmadi)", "en": "Theme (button color)", "de": "Design (Schaltflachenfarbe)",
        "sk": "Motiv (farba tlacidiel)", "uk": "Тема (колір кнопок)", "it": "Tema (colore pulsanti)",
        "fr": "Theme (couleur des boutons)", "bg": "Тема (цвят на бутоните)",
    },
    "podesavanja_pozadina_btn": {
        "sr": "Boja pozadine ekrana", "en": "Screen background color", "de": "Bildschirmhintergrundfarbe",
        "sk": "Farba pozadia obrazovky", "uk": "Колір фону екрана", "it": "Colore sfondo schermo",
        "fr": "Couleur de fond de l'ecran", "bg": "Цвят на фона на екрана",
    },
    "podesavanja_tekst_btn": {
        "sr": "Boja teksta u poljima", "en": "Input field text color", "de": "Textfarbe der Eingabefelder",
        "sk": "Farba textu v poliach", "uk": "Колір тексту в полях", "it": "Colore testo dei campi",
        "fr": "Couleur du texte des champs", "bg": "Цвят на текста в полетата",
    },
    "podesavanja_kurs_btn": {
        "sr": "Kurs", "en": "Exchange rate", "de": "Wechselkurs", "sk": "Kurz",
        "uk": "Курс", "it": "Tasso di cambio", "fr": "Taux de change", "bg": "Валутен курс",
    },
    "podesavanja_tema_naslov": {
        "sr": "Tema", "en": "Theme", "de": "Design", "sk": "Motiv",
        "uk": "Тема", "it": "Tema", "fr": "Theme", "bg": "Тема",
    },
    "podesavanja_pozadina_naslov": {
        "sr": "Boja pozadine", "en": "Background color", "de": "Hintergrundfarbe", "sk": "Farba pozadia",
        "uk": "Колір фону", "it": "Colore di sfondo", "fr": "Couleur de fond", "bg": "Цвят на фона",
    },
    "podesavanja_tekst_naslov": {
        "sr": "Boja teksta u poljima", "en": "Input field text color", "de": "Textfarbe der Eingabefelder",
        "sk": "Farba textu v poliach", "uk": "Колір тексту в полях", "it": "Colore testo dei campi",
        "fr": "Couleur du texte des champs", "bg": "Цвят на текста в полетата",
    },
    "podesavanja_kurs_naslov": {
        "sr": "Kurs", "en": "Exchange rate", "de": "Wechselkurs", "sk": "Kurz",
        "uk": "Курс", "it": "Tasso di cambio", "fr": "Taux de change", "bg": "Валутен курс",
    },
    "podesavanja_aktivno": {
        "sr": "(aktivno)", "en": "(active)", "de": "(aktiv)", "sk": "(aktivne)",
        "uk": "(активний)", "it": "(attivo)", "fr": "(actif)", "bg": "(активен)",
    },
    "podesavanja_boja_zauzeta": {
        "sr": "Ta boja je vec zauzeta drugde.", "en": "That color is already used elsewhere.",
        "de": "Diese Farbe wird bereits an anderer Stelle verwendet.", "sk": "Tato farba sa uz pouziva inde.",
        "uk": "Цей колір вже використовується деінде.", "it": "Questo colore e gia usato altrove.",
        "fr": "Cette couleur est deja utilisee ailleurs.", "bg": "Този цвят вече се използва другаде.",
    },
    "podesavanja_zatvori": {
        "sr": "Zatvori", "en": "Close", "de": "Schliessen", "sk": "Zatvorit",
        "uk": "Закрити", "it": "Chiudi", "fr": "Fermer", "bg": "Затвори",
    },
    "podesavanja_kurs_info": {
        "sr": "Ovaj kurs se koristi samo kad rucno zatrazis prikaz u drugoj valuti (npr. u pregledu Troskova). Svaka stavka i dalje cuva svoju valutu onako kako je uneta.",
        "en": "This rate is used only when you manually request a display in another currency (e.g. in the Expenses overview). Each item still keeps its own currency as entered.",
        "de": "Dieser Kurs wird nur verwendet, wenn Sie manuell eine Anzeige in einer anderen Wahrung anfordern (z.B. in der Ausgabenubersicht). Jeder Eintrag behalt weiterhin seine eigene, eingegebene Wahrung.",
        "sk": "Tento kurz sa pouziva iba vtedy, ked rucne poziadate o zobrazenie v inej mene (napr. v prehlade Nakladov). Kazda polozka si stale zachovava svoju vlastnu zadanu menu.",
        "uk": "Цей курс використовується лише коли ви вручну запитуєте відображення в іншій валюті (напр. в огляді Витрат). Кожен запис зберігає свою власну введену валюту.",
        "it": "Questo tasso viene usato solo quando richiedi manualmente la visualizzazione in un'altra valuta (es. nella panoramica Spese). Ogni voce mantiene comunque la propria valuta cosi come inserita.",
        "fr": "Ce taux n'est utilise que lorsque vous demandez manuellement un affichage dans une autre devise (par ex. dans l'apercu des Depenses). Chaque element conserve sa propre devise telle que saisie.",
        "bg": "Този курс се използва само когато ръчно поискате показване в друга валута (напр. в прегледа на Разходите). Всеки запис запазва своята въведена валута.",
    },
    "podesavanja_kurs_label": {
        "sr": "Kurs (1 EUR = ? RSD)", "en": "Rate (1 EUR = ? RSD)", "de": "Kurs (1 EUR = ? RSD)",
        "sk": "Kurz (1 EUR = ? RSD)", "uk": "Курс (1 EUR = ? RSD)", "it": "Tasso (1 EUR = ? RSD)",
        "fr": "Taux (1 EUR = ? RSD)", "bg": "Курс (1 EUR = ? RSD)",
    },
    "podesavanja_backup_btn": {
        "sr": "Sacuvaj rezervnu kopiju", "en": "Save backup", "de": "Sicherung speichern",
        "sk": "Ulozit zalohu", "uk": "Зберегти резервну копію", "it": "Salva backup",
        "fr": "Enregistrer la sauvegarde", "bg": "Запази резервно копие",
    },
    "podesavanja_restore_btn": {
        "sr": "Vrati rezervnu kopiju", "en": "Restore backup", "de": "Sicherung wiederherstellen",
        "sk": "Obnovit zalohu", "uk": "Відновити резервну копію", "it": "Ripristina backup",
        "fr": "Restaurer la sauvegarde", "bg": "Възстанови резервно копие",
    },
    "podesavanja_backup_sacuvan": {
        "sr": "Rezervna kopija sacuvana: {putanja}", "en": "Backup saved: {putanja}",
        "de": "Sicherung gespeichert: {putanja}", "sk": "Zaloha ulozena: {putanja}",
        "uk": "Резервну копію збережено: {putanja}", "it": "Backup salvato: {putanja}",
        "fr": "Sauvegarde enregistree: {putanja}", "bg": "Резервното копие е запазено: {putanja}",
    },
    "podesavanja_backup_vracen": {
        "sr": "Podaci su uspesno vraceni. Ponovo otvori aplikaciju.",
        "en": "Data restored successfully. Reopen the app.",
        "de": "Daten erfolgreich wiederhergestellt. App erneut offnen.",
        "sk": "Data boli uspesne obnovene. Znovu otvorte aplikaciu.",
        "uk": "Дані успішно відновлено. Відкрийте застосунок знову.",
        "it": "Dati ripristinati con successo. Riapri l'app.",
        "fr": "Donnees restaurees avec succes. Rouvrez l'application.",
        "bg": "Данните са възстановени успешно. Отворете отново приложението.",
    },
    "podesavanja_backup_nema": {
        "sr": "Nije pronadjena rezervna kopija u Download folderu.",
        "en": "No backup found in the Download folder.",
        "de": "Keine Sicherung im Download-Ordner gefunden.",
        "sk": "V priecinku Download nebola najdena ziadna zaloha.",
        "uk": "У папці Завантаження не знайдено резервної копії.",
        "it": "Nessun backup trovato nella cartella Download.",
        "fr": "Aucune sauvegarde trouvee dans le dossier Download.",
        "bg": "В папка Download не е намерено резервно копие.",
    },
    "podesavanja_backup_greska": {
        "sr": "Greska: {greska}", "en": "Error: {greska}", "de": "Fehler: {greska}",
        "sk": "Chyba: {greska}", "uk": "Помилка: {greska}", "it": "Errore: {greska}",
        "fr": "Erreur: {greska}", "bg": "Грешка: {greska}",
    },
    "dokumenti_slikaj_btn": {
        "sr": "Slikaj dokument", "en": "Take photo", "de": "Dokument fotografieren",
        "sk": "Odfotit dokument", "uk": "Сфотографувати документ", "it": "Fotografa documento",
        "fr": "Photographier le document", "bg": "Снимай документа",
    },
    "dokumenti_nema_slike": {
        "sr": "Nema slike jos.", "en": "No photo yet.", "de": "Noch kein Foto.",
        "sk": "Zatial ziadna fotka.", "uk": "Ще немає фото.", "it": "Nessuna foto ancora.",
        "fr": "Pas encore de photo.", "bg": "Все още няма снимка.",
    },
    "dokumenti_slika_snimljena": {
        "sr": "Slika snimljena.", "en": "Photo saved.", "de": "Foto gespeichert.",
        "sk": "Fotka ulozena.", "uk": "Фото збережено.", "it": "Foto salvata.",
        "fr": "Photo enregistree.", "bg": "Снимката е запазена.",
    },
    "dokumenti_greska_slikanja": {
        "sr": "Slikanje nije uspelo.", "en": "Taking photo failed.", "de": "Fotografieren fehlgeschlagen.",
        "sk": "Fotenie zlyhalo.", "uk": "Не вдалося сфотографувати.", "it": "Scatto foto non riuscito.",
        "fr": "Echec de la prise de photo.", "bg": "Снимането не бе успешно.",
    },
    "dokumenti_kamera_nedostupna": {
        "sr": "Kamera nije dostupna na ovom uredjaju.", "en": "Camera not available on this device.",
        "de": "Kamera auf diesem Gerat nicht verfugbar.", "sk": "Fotoaparat nie je na tomto zariadeni dostupny.",
        "uk": "Камера недоступна на цьому пристрої.", "it": "Fotocamera non disponibile su questo dispositivo.",
        "fr": "Camera non disponible sur cet appareil.", "bg": "Камерата не е достъпна на това устройство.",
    },
    "dokumenti_greska_naziv": {
        "sr": "Unesi naziv dokumenta.", "en": "Enter a document name.", "de": "Dokumentnamen eingeben.",
        "sk": "Zadajte nazov dokumentu.", "uk": "Введіть назву документа.", "it": "Inserisci il nome del documento.",
        "fr": "Entrez le nom du document.", "bg": "Въведете име на документа.",
    },
    "dokumenti_greska_slika": {
        "sr": "Prvo slikaj dokument.", "en": "Take a photo first.", "de": "Zuerst ein Foto machen.",
        "sk": "Najprv odfotte dokument.", "uk": "Спочатку сфотографуйте документ.", "it": "Prima scatta una foto.",
        "fr": "Prenez d'abord une photo.", "bg": "Първо снимай документа.",
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

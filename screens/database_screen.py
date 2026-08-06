from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime, timedelta
import calendar

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput
import pdf_report


Builder.load_string("""
<IconTabButton>:
    orientation: "vertical"
    padding: dp(4)
    spacing: dp(2)
    canvas.before:
        Color:
            rgba: 0.14, 0.14, 0.17, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
    canvas.after:
        Color:
            rgba: (0, 0, 0, 0.45) if self.state == "down" else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
    Image:
        source: root.icon_source
        allow_stretch: True
        keep_ratio: True
        size_hint_y: 0.65
    Label:
        text: root.text
        font_size: "11sp"
        bold: True
        size_hint_y: 0.35
""")


class IconTabButton(ButtonBehavior, BoxLayout):
    """Dugme sa ikonicom iznad teksta, koristi se za tabove
    (Gorivo/Servisi/Troskovi i Gume/Registracija/Osiguranje/
    Akumulator/Kvarovi/Dokumenta/Podsetnici/PDF)."""

    icon_source = StringProperty("")
    text = StringProperty("")


KATEGORIJE_TROSKOVA = [
    ("gorivo", "Gorivo"),
    ("servisi", "Servisi"),
    ("osiguranje", "Osiguranje"),
    ("troskovi", "Ostali troskovi"),
]

TABELE_SA_VALUTOM = {
    "gorivo", "servisi", "troskovi", "gume",
    "registracija", "osiguranje", "akumulator", "kvarovi",
}


class DatabaseScreen(Screen):
    """
    Ekran za unos zapisa po vozilu, sa tabovima: Gorivo, Servisi,
    Troskovi (glavna 3 dugmeta iz kv fajla) i Gume, Registracija,
    Osiguranje, Akumulator, Kvarovi, Dokumenta, Podsetnici, PDF
    (dinamicki dodati u extra_tabs_box, sa ikonicama).

    Napomena o valuti: svaka novcana stavka bira svoju valutu (RSD ili
    EUR) prilikom unosa - ta valuta se cuva uz stavku i koristi se za
    prikaz, bez automatske konverzije. Pregled Troskova ima dugme za
    RUCNO prebacivanje prikaza zbira izmedju RSD i EUR (koristi kurs
    iz Podesavanja samo za taj prikaz).
    """

    PDF_TAB_KEY = "pdf"
    TROSKOVI_TAB_KEY = "troskovi"

    TAB_DEFS = {
        "gorivo": {
            "naslov": "Gorivo",
            "fields": [
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("kilometraza", "Kilometraza", "int"),
                ("litara", "Litara", "float"),
                ("cena_po_litru", "Cena po litru", "float"),
                ("pumpa", "Pumpa", "text"),
                ("grad", "Grad", "text"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - {r['litara']} L - "
                f"{r['ukupna_cena']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "servisi": {
            "naslov": "Servisi",
            "fields": [
                ("tip", "Tip servisa", "text"),
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("kilometraza", "Kilometraza", "int"),
                ("naziv", "Naziv", "text"),
                ("opis", "Opis", "text"),
                ("cena_delova", "Cena delova", "float"),
                ("cena_rada", "Cena rada", "float"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - {r['tip']} - "
                f"{r['ukupna_cena']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "troskovi": {
            "naslov": "Troskovi",
            "fields": [
                ("vrsta", "Vrsta troska", "text"),
                ("iznos", "Iznos", "float"),
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("napomena", "Napomena", "text"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - {r['vrsta']} - "
                f"{r['iznos']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "gume": {
            "naslov": "Gume",
            "fields": [
                ("sezona", "Sezona (letnje/zimske)", "text"),
                ("marka", "Marka", "text"),
                ("model", "Model", "text"),
                ("dimenzija", "Dimenzija", "text"),
                ("dot", "DOT", "text"),
                ("cena", "Cena", "float"),
                ("datum_kupovine", "Datum kupovine (DD.MM.GGGG)", "text"),
                ("kilometraza_montaze", "Kilometraza montaze", "int"),
                ("napomena", "Napomena", "text"),
            ],
            "prikaz": lambda r: f"{r['sezona']} - {r['marka'] or '-'} {r['model'] or '-'} ({r['dimenzija'] or '-'})",
        },
        "registracija": {
            "naslov": "Registracija",
            "fields": [
                ("datum_registracije", "Datum registracije (DD.MM.GGGG)", "text"),
                ("istek", "Istek (DD.MM.GGGG)", "text"),
                ("cena", "Cena", "float"),
                ("tehnicki_pregled", "Tehnicki pregled", "text"),
                ("napomena", "Napomena", "text"),
            ],
            "prikaz": lambda r: f"{r['datum_registracije'] or '-'} - istice {r['istek'] or '-'}",
        },
        "osiguranje": {
            "naslov": "Osiguranje",
            "fields": [
                ("vrsta", "Vrsta osiguranja", "text"),
                ("cena", "Cena", "float"),
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("istek", "Istek (DD.MM.GGGG)", "text"),
            ],
            "prikaz": lambda r: f"{r['vrsta'] or '-'} - istice {r['istek'] or '-'}",
        },
        "akumulator": {
            "naslov": "Akumulator",
            "fields": [
                ("marka", "Marka", "text"),
                ("model", "Model", "text"),
                ("kapacitet", "Kapacitet", "text"),
                ("datum_kupovine", "Datum kupovine (DD.MM.GGGG)", "text"),
                ("cena", "Cena", "float"),
                ("garancija", "Garancija", "text"),
            ],
            "prikaz": lambda r: f"{r['marka'] or '-'} {r['model'] or '-'} - {r['kapacitet'] or '-'}",
        },
        "kvarovi": {
            "naslov": "Kvarovi",
            "fields": [
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("kilometraza", "Kilometraza", "int"),
                ("opis", "Opis", "text"),
                ("cena_rada", "Cena rada", "float"),
                ("cena_delova", "Cena delova", "float"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - "
                f"{r['ukupna_cena']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "dokumenti": {
            "naslov": "Dokumenta",
            "fields": [
                ("tip", "Tip dokumenta", "text"),
                ("naziv", "Naziv", "text"),
                ("putanja", "Putanja/naziv fajla", "text"),
                ("datum_dodavanja", "Datum dodavanja (DD.MM.GGGG)", "text"),
            ],
            "prikaz": lambda r: f"{r['tip']} - {r['naziv'] or '-'}",
        },
        "podsetnici": {
            "naslov": "Podsetnici",
            "fields": [
                ("tip", "Tip podsetnika (npr. registracija, servis)", "text"),
                ("naslov", "Naslov", "text"),
                ("datum_isteka", "Datum isteka (DD.MM.GGGG)", "text"),
                ("kilometraza_isteka", "Kilometraza isteka", "int"),
            ],
            "prikaz": lambda r: f"{r['naslov'] or r['tip']} - istice {r['datum_isteka'] or '-'}",
        },
    }

    EXTRA_TAB_ICONS = {
        "gume": ("gume.png", "Gume"),
        "registracija": ("registracija.png", "Registracija"),
        "osiguranje": ("osiguranje.png", "Osiguranje"),
        "akumulator": ("akumulator.png", "Akumulator"),
        "kvarovi": ("kvarovi.png", "Kvarovi"),
        "dokumenti": ("dokumenti.png", "Dokumenta"),
        "podsetnici": ("podsetnici.png", "Podsetnici"),
        "pdf": ("pdf_izvestaji.png", "PDF"),
    }

    def on_pre_enter(self, *args):
        self.ids.title_label.text = "Zapisi vozila"
        self.ids.tab_products.text = "Gorivo"
        self.ids.tab_stores.text = "Servisi"
        self.ids.tab_categories.text = "Troskovi"
        self._build_extra_tabs()
        self.show_proizvodi()

    # ---------- Dodatni tabovi (dinamicki, sa ikonicama, u extra_tabs_box) ----------

    def _build_extra_tabs(self):
        box = self.ids.extra_tabs_box
        box.clear_widgets()
        assets_dir = App.get_running_app().assets_dir
        for tabela, (icon_fajl, naslov) in self.EXTRA_TAB_ICONS.items():
            btn = IconTabButton(
                icon_source=assets_dir + icon_fajl,
                text=naslov,
            )
            btn.bind(on_release=lambda inst, t=tabela: self._prikazi_vozila_za_tab(t))
            box.add_widget(btn)

    # ---------- Tabovi (nazivi metoda zadrzani zbog kv fajla) ----------

    def show_proizvodi(self):
        self._prikazi_vozila_za_tab("gorivo")

    def show_prodavnice(self):
        self._prikazi_vozila_za_tab("servisi")

    def show_kategorije(self):
        self._prikazi_vozila_za_tab("troskovi")

    def _prikazi_vozila_za_tab(self, tabela):
        box = self.ids.database_box
        box.clear_widgets()

        vozila = db.get_all("vozila", order_by="marka")
        if not vozila:
            box.add_widget(Label(
                text="Nema dodatih vozila.", size_hint_y=None,
                height=dp(40), color=(1, 1, 1, 1),
            ))
            return

        for vozilo in vozila:
            btn = Button(
                text=f"{vozilo['marka']} {vozilo['model']}",
                size_hint_y=None, height=dp(46),
                background_normal="", background_color=(0.18, 0.18, 0.22, 1),
                color=(1, 1, 1, 1),
            )
            if tabela == self.PDF_TAB_KEY:
                btn.bind(
                    on_release=lambda inst, vid=vozilo["id"]: self._generisi_pdf(vid)
                )
            elif tabela == self.TROSKOVI_TAB_KEY:
                btn.bind(
                    on_release=lambda inst, vid=vozilo["id"], vnaziv=f"{vozilo['marka']} {vozilo['model']}":
                        self.open_troskovi_pregled(vid, vnaziv)
                )
            else:
                btn.bind(
                    on_release=lambda inst, vid=vozilo["id"], vnaziv=f"{vozilo['marka']} {vozilo['model']}":
                        self.open_records_popup(tabela, vid, vnaziv)
                )
            box.add_widget(btn)

    # ---------- PDF izvestaj ----------

    def _generisi_pdf(self, vehicle_id):
        vozilo = db.get_by_id("vozila", vehicle_id)
        if vozilo is None:
            return

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
        popup = Popup(
            title="PDF izvestaj", content=content, size_hint=(0.85, 0.45),
            overlay_color=(0, 0, 0, 0.85),
        )

        try:
            pdf_report.generisi_pdf_izvestaj(vozilo)
            poruka = "PDF je generisan.\n\nIdite u Download da pogledate i stampate ako vam je potreban."
        except Exception as e:
            poruka = f"Greska pri pravljenju PDF-a:\n{e}"

        poruka_label = Label(
            text=poruka,
            font_size="14sp",
            halign="center",
            valign="middle",
        )
        poruka_label.bind(
            size=lambda inst, val: setattr(inst, "text_size", val)
        )
        content.add_widget(poruka_label)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    # ---------- Troskovi: pregled po periodu, sa rucnim prebacivanjem prikazne valute ----------

    def _prikazi_zbir_u_box(self, box, naslov, zbir, prikaz_valuta):
        box.add_widget(Label(
            text=naslov, bold=True, font_size="15sp",
            size_hint_y=None, height=dp(26),
        ))
        for kljuc, label in KATEGORIJE_TROSKOVA:
            box.add_widget(Label(
                text=f"{label}: {zbir[kljuc]:.2f} {prikaz_valuta}",
                font_size="13sp", size_hint_y=None, height=dp(22),
            ))
        box.add_widget(Label(
            text=f"UKUPNO: {zbir['ukupno']:.2f} {prikaz_valuta}",
            bold=True, font_size="14sp", size_hint_y=None, height=dp(26),
            color=(0.6, 0.85, 1, 1),
        ))

    def _godine_sa_podacima(self, vehicle_id):
        godine = {datetime.now().year}
        for tabela, polje in (
            ("gorivo", "datum"), ("servisi", "datum"),
            ("osiguranje", "datum"), ("troskovi", "datum"),
        ):
            for red in db.get_by_vehicle(tabela, vehicle_id):
                d = red[polje]
                if d:
                    try:
                        godine.add(datetime.strptime(d.strip(), "%d.%m.%Y").year)
                    except ValueError:
                        pass
        return sorted(godine, reverse=True)

    def open_troskovi_pregled(self, vehicle_id, vozilo_naziv):
        prikaz_stanje = {"valuta": "RSD"}

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(
            text=vozilo_naziv, bold=True, font_size="18sp",
            size_hint_y=None, height=dp(30),
        ))

        prebaci_btn = PrimaryButton(
            text="Prikazi u EUR", size_hint_y=None, height=dp(44),
        )
        content.add_widget(prebaci_btn)

        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        inner.bind(minimum_height=inner.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(inner)
        content.add_widget(scroll)

        popup = Popup(
            title="Pregled troskova", content=content, size_hint=(0.94, 0.9),
            overlay_color=(0, 0, 0, 0.85),
        )

        izabrani_period = {"tip": None, "godina": None, "mesec": None}

        def iscrtaj_sve():
            inner.clear_widgets()
            pv = prikaz_stanje["valuta"]
            danas = datetime.now()

            pocetak_nedelje = danas - timedelta(days=danas.weekday())
            pocetak_nedelje = pocetak_nedelje.replace(hour=0, minute=0, second=0)
            kraj_nedelje = pocetak_nedelje + timedelta(days=6, hours=23, minutes=59, seconds=59)
            zbir_nedelja = db.troskovi_pregled(vehicle_id, pocetak_nedelje, kraj_nedelje, pv)
            self._prikazi_zbir_u_box(inner, "Ova nedelja", zbir_nedelja, pv)

            pocetak_meseca = danas.replace(day=1, hour=0, minute=0, second=0)
            poslednji_dan_meseca = calendar.monthrange(danas.year, danas.month)[1]
            kraj_meseca = danas.replace(day=poslednji_dan_meseca, hour=23, minute=59, second=59)
            zbir_mesec = db.troskovi_pregled(vehicle_id, pocetak_meseca, kraj_meseca, pv)
            self._prikazi_zbir_u_box(inner, "Ovaj mesec", zbir_mesec, pv)

            pocetak_godine = danas.replace(month=1, day=1, hour=0, minute=0, second=0)
            kraj_godine = danas.replace(month=12, day=31, hour=23, minute=59, second=59)
            zbir_godina = db.troskovi_pregled(vehicle_id, pocetak_godine, kraj_godine, pv)
            self._prikazi_zbir_u_box(inner, "Ova godina", zbir_godina, pv)

            if izabrani_period["tip"] == "mesec":
                g, m = izabrani_period["godina"], izabrani_period["mesec"]
                prvi = datetime(g, m, 1)
                poslednji_dan = calendar.monthrange(g, m)[1]
                poslednji = datetime(g, m, poslednji_dan, 23, 59, 59)
                naziv_meseca = prvi.strftime("%B %Y")
                zbir = db.troskovi_pregled(vehicle_id, prvi, poslednji, pv)
                self._prikazi_zbir_u_box(inner, f"Izabrano: {naziv_meseca}", zbir, pv)
            elif izabrani_period["tip"] == "godina":
                g = izabrani_period["godina"]
                prvi = datetime(g, 1, 1)
                poslednji = datetime(g, 12, 31, 23, 59, 59)
                zbir = db.troskovi_pregled(vehicle_id, prvi, poslednji, pv)
                self._prikazi_zbir_u_box(inner, f"Izabrano: godina {g}", zbir, pv)

        def prebaci_valutu(*a):
            prikaz_stanje["valuta"] = "EUR" if prikaz_stanje["valuta"] == "RSD" else "RSD"
            prebaci_btn.text = "Prikazi u RSD" if prikaz_stanje["valuta"] == "EUR" else "Prikazi u EUR"
            iscrtaj_sve()

        prebaci_btn.bind(on_release=prebaci_valutu)

        def open_mesec_picker(*a):
            godine = self._godine_sa_podacima(vehicle_id)
            pick_content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10))
            pick_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
            pick_box.bind(minimum_height=pick_box.setter("height"))
            pick_scroll = ScrollView(size_hint_y=1)
            pick_scroll.add_widget(pick_box)
            pick_content.add_widget(pick_scroll)

            pick_popup = Popup(
                title="Izaberi godinu", content=pick_content, size_hint=(0.8, 0.7),
                overlay_color=(0, 0, 0, 0.85),
            )

            def izabrana_godina(g):
                pick_popup.dismiss()
                open_mesec_picker_za_godinu(g)

            for g in godine:
                btn = SecondaryButton(text=str(g), size_hint_y=None, height=dp(44))
                btn.bind(on_release=lambda inst, gg=g: izabrana_godina(gg))
                pick_box.add_widget(btn)

            close_btn = SecondaryButton(text="Otkazi", size_hint_y=None, height=dp(44))
            close_btn.bind(on_release=pick_popup.dismiss)
            pick_content.add_widget(close_btn)

            pick_popup.open()

        def open_mesec_picker_za_godinu(godina):
            nazivi_meseci = [
                "Januar", "Februar", "Mart", "April", "Maj", "Jun",
                "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar",
            ]
            pick_content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10))
            pick_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
            pick_box.bind(minimum_height=pick_box.setter("height"))
            pick_scroll = ScrollView(size_hint_y=1)
            pick_scroll.add_widget(pick_box)
            pick_content.add_widget(pick_scroll)

            pick_popup = Popup(
                title=f"Izaberi mesec ({godina})", content=pick_content, size_hint=(0.8, 0.85),
                overlay_color=(0, 0, 0, 0.85),
            )

            def izabran(m):
                pick_popup.dismiss()
                izabrani_period["tip"] = "mesec"
                izabrani_period["godina"] = godina
                izabrani_period["mesec"] = m
                iscrtaj_sve()

            for i, naziv in enumerate(nazivi_meseci, start=1):
                btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
                btn.bind(on_release=lambda inst, m=i: izabran(m))
                pick_box.add_widget(btn)

            close_btn = SecondaryButton(text="Otkazi", size_hint_y=None, height=dp(44))
            close_btn.bind(on_release=pick_popup.dismiss)
            pick_content.add_widget(close_btn)

            pick_popup.open()

        def open_godina_picker(*a):
            godine = self._godine_sa_podacima(vehicle_id)
            pick_content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10))
            pick_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
            pick_box.bind(minimum_height=pick_box.setter("height"))
            pick_scroll = ScrollView(size_hint_y=1)
            pick_scroll.add_widget(pick_box)
            pick_content.add_widget(pick_scroll)

            pick_popup = Popup(
                title="Izaberi godinu", content=pick_content, size_hint=(0.8, 0.7),
                overlay_color=(0, 0, 0, 0.85),
            )

            def izabrana(g):
                pick_popup.dismiss()
                izabrani_period["tip"] = "godina"
                izabrani_period["godina"] = g
                iscrtaj_sve()

            for g in godine:
                btn = SecondaryButton(text=str(g), size_hint_y=None, height=dp(44))
                btn.bind(on_release=lambda inst, gg=g: izabrana(gg))
                pick_box.add_widget(btn)

            close_btn = SecondaryButton(text="Otkazi", size_hint_y=None, height=dp(44))
            close_btn.bind(on_release=pick_popup.dismiss)
            pick_content.add_widget(close_btn)

            pick_popup.open()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        mesec_btn = PrimaryButton(text="Izaberi mesec")
        mesec_btn.bind(on_release=open_mesec_picker)
        godina_btn = PrimaryButton(text="Izaberi godinu")
        godina_btn.bind(on_release=open_godina_picker)
        btn_row.add_widget(mesec_btn)
        btn_row.add_widget(godina_btn)
        content.add_widget(btn_row)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        iscrtaj_sve()
        popup.open()

    # ---------- Zapisi jednog vozila (za dati tab) ----------

    def open_records_popup(self, tabela, vehicle_id, vozilo_naziv):
        tab_def = self.TAB_DEFS[tabela]
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        content.add_widget(Label(
            text=f"{vozilo_naziv} - {tab_def['naslov']}", bold=True, font_size="18sp",
            size_hint_y=None, height=dp(32),
        ))

        records_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        records_box.bind(minimum_height=records_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(records_box)
        content.add_widget(scroll)

        popup = Popup(
            title=tab_def["naslov"], content=content, size_hint=(0.94, 0.85),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            records_box.clear_widgets()
            zapisi = db.get_by_vehicle(tabela, vehicle_id, order_by="id DESC")
            if not zapisi:
                records_box.add_widget(Label(
                    text="Nema zapisa.", size_hint_y=None,
                    height=dp(36), color=(0.75, 0.75, 0.75, 1),
                ))
            for red in zapisi:
                btn = SecondaryButton(
                    text=tab_def["prikaz"](red), size_hint_y=None, height=dp(52),
                )
                btn.bind(
                    on_release=lambda inst, rid=red["id"]:
                        self.open_edit_record_popup(tabela, rid, vehicle_id, popup, refresh)
                )
                records_box.add_widget(btn)

        novi_btn = PrimaryButton(text="+ Dodaj zapis", size_hint_y=None, height=dp(44))
        novi_btn.bind(
            on_release=lambda inst: self.open_add_record_popup(tabela, vehicle_id, popup, refresh)
        )
        content.add_widget(novi_btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    # ---------- Dodavanje / izmena zapisa ----------

    def _build_form(self, tabela, existing=None, valuta_stanje=None):
        tab_def = self.TAB_DEFS[tabela]
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        if tabela in TABELE_SA_VALUTOM:
            pocetna_valuta = "RSD"
            if existing is not None and existing["valuta"]:
                pocetna_valuta = existing["valuta"]
            valuta_stanje["valuta"] = pocetna_valuta

            valuta_btn = PrimaryButton(
                text=f"Valuta: {pocetna_valuta}", size_hint_y=None, height=dp(44),
            )

            def promeni_valutu(*a):
                valuta_stanje["valuta"] = "EUR" if valuta_stanje["valuta"] == "RSD" else "RSD"
                valuta_btn.text = f"Valuta: {valuta_stanje['valuta']}"

            valuta_btn.bind(on_release=promeni_valutu)
            content.add_widget(valuta_btn)

        inputs = {}
        for key, label, tip in tab_def["fields"]:
            vrednost = ""
            if existing is not None and existing[key] is not None:
                vrednost = str(existing[key])
            tf = StyledTextInput(
                text=vrednost, hint_text=label,
                input_filter=("float" if tip == "float" else "int" if tip == "int" else None),
                multiline=False, size_hint_y=None, height=dp(44),
            )
            inputs[key] = tf
            content.add_widget(tf)

        return content, inputs

    def _collect_data(self, tabela, inputs, valuta_stanje=None):
        tab_def = self.TAB_DEFS[tabela]
        data = {}
        for key, _label, tip in tab_def["fields"]:
            tekst = inputs[key].text.strip()
            if tip == "int":
                data[key] = int(tekst) if tekst else 0
            elif tip == "float":
                data[key] = float(tekst.replace(",", ".")) if tekst else 0.0
            else:
                data[key] = tekst
        if tabela in TABELE_SA_VALUTOM and valuta_stanje is not None:
            data["valuta"] = valuta_stanje["valuta"]
        return data

    def open_add_record_popup(self, tabela, vehicle_id, parent_popup, refresh_parent):
        valuta_stanje = {}
        content, inputs = self._build_form(tabela, valuta_stanje=valuta_stanje)
        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        scroll_wrap = ScrollView(size_hint=(1, None), height=dp(400))
        scroll_wrap.add_widget(content)
        outer = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        outer.add_widget(scroll_wrap)

        popup = Popup(
            title="Novi zapis", content=outer, size_hint=(0.9, 0.85),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            data = self._collect_data(tabela, inputs, valuta_stanje)
            if tabela == "gorivo":
                data["ukupna_cena"] = round(data.get("litara", 0) * data.get("cena_po_litru", 0), 2)
                data["pun_rezervoar"] = 1
            elif tabela == "servisi":
                data["ukupna_cena"] = round(data.get("cena_delova", 0) + data.get("cena_rada", 0), 2)
            elif tabela == "kvarovi":
                data["ukupna_cena"] = round(data.get("cena_rada", 0) + data.get("cena_delova", 0), 2)
            elif tabela == "podsetnici":
                data["aktivan"] = 1
            data["vehicle_id"] = vehicle_id
            db.insert(tabela, data)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        outer.add_widget(btn_row)

        popup.open()

    def open_edit_record_popup(self, tabela, record_id, vehicle_id, parent_popup, refresh_parent):
        red = db.get_by_id(tabela, record_id)
        if red is None:
            return

        valuta_stanje = {}
        content, inputs = self._build_form(tabela, existing=red, valuta_stanje=valuta_stanje)
        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        scroll_wrap = ScrollView(size_hint=(1, None), height=dp(400))
        scroll_wrap.add_widget(content)
        outer = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        outer.add_widget(scroll_wrap)

        popup = Popup(
            title="Izmeni zapis", content=outer, size_hint=(0.9, 0.85),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            data = self._collect_data(tabela, inputs, valuta_stanje)
            if tabela == "gorivo":
                data["ukupna_cena"] = round(data.get("litara", 0) * data.get("cena_po_litru", 0), 2)
            elif tabela == "servisi":
                data["ukupna_cena"] = round(data.get("cena_delova", 0) + data.get("cena_rada", 0), 2)
            elif tabela == "kvarovi":
                data["ukupna_cena"] = round(data.get("cena_rada", 0) + data.get("cena_delova", 0), 2)
            db.update(tabela, record_id, data)
            popup.dismiss()
            refresh_parent()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = "Potvrdi brisanje"
                return
            db.delete(tabela, record_id)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        outer.add_widget(btn_row)

        delete_btn = DangerButton(text="Obrisi zapis", size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        outer.add_widget(delete_btn)

        popup.open()

    def go_back(self):
        self.manager.current = "home"

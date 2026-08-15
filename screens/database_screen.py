from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from datetime import datetime, timedelta
import calendar
import time
import os
import threading

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput
from translations import prevedi
import pdf_report
import ocr_racun


def _jezik():
    return db.get_setting("jezik", "sr")


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
    ("gorivo", "kat_gorivo"),
    ("servisi", "kat_servisi"),
    ("osiguranje", "kat_osiguranje"),
    ("troskovi", "kat_troskovi"),
]

TABELE_SA_VALUTOM = {
    "gorivo", "servisi", "troskovi", "gume",
    "registracija", "osiguranje", "akumulator", "kvarovi",
}

BOJA_NEIZABRANO = (0.18, 0.18, 0.22, 1)
BOJA_IZABRANO = (0.2, 0.5, 1, 1)

NASLOVI = {
    "gorivo": "kat_gorivo",
    "servisi": "kat_servisi",
    "troskovi": "kat_troskovi",
    "gume": "kat_gume",
    "registracija": "kat_registracija",
    "osiguranje": "kat_osiguranje",
    "akumulator": "kat_akumulator",
    "kvarovi": "kat_kvarovi",
    "dokumenti": "kat_dokumenta",
    "podsetnici": "kat_podsetnici",
}


class DatabaseScreen(Screen):
    """
    Ekran za unos zapisa po vozilu. Redosled je: prvo se BIRA VOZILO
    iz liste (dugme postaje plavo kad je izabrano), a zatim se klikom
    na kategoriju gore (Gorivo/Servisi/Troskovi ili donje ikonice)
    otvara odgovarajuci prozor za TO izabrano vozilo. Tekstovi se
    prevode preko translations.prevedi() prema trenutno izabranom
    jeziku.
    """

    PDF_TAB_KEY = "pdf"
    TROSKOVI_TAB_KEY = "troskovi"

    TAB_DEFS = {
        "gorivo": {
            "fields": [
                ("datum", "polje_datum", "text"),
                ("kilometraza", "polje_kilometraza", "int"),
                ("litara", "polje_litara", "float"),
                ("cena_po_litru", "polje_cena_po_litru", "float"),
                ("pumpa", "polje_pumpa", "text"),
                ("grad", "polje_grad", "text"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - {r['litara']} L - "
                f"{r['ukupna_cena']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "servisi": {
            "fields": [
                ("tip", "polje_tip_servisa", "text"),
                ("datum", "polje_datum", "text"),
                ("kilometraza", "polje_kilometraza", "int"),
                ("naziv", "polje_naziv", "text"),
                ("opis", "polje_opis", "text"),
                ("cena_delova", "polje_cena_delova", "float"),
                ("cena_rada", "polje_cena_rada", "float"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - {r['tip']} - "
                f"{r['ukupna_cena']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "troskovi": {
            "fields": [
                ("vrsta", "polje_vrsta_troska", "text"),
                ("iznos", "polje_iznos", "float"),
                ("datum", "polje_datum", "text"),
                ("napomena", "polje_napomena", "text"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - {r['vrsta']} - "
                f"{r['iznos']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "gume": {
            "fields": [
                ("sezona", "polje_sezona", "text"),
                ("marka", "polje_marka", "text"),
                ("model", "polje_model", "text"),
                ("dimenzija", "polje_dimenzija", "text"),
                ("dot", "polje_dot", "text"),
                ("cena", "polje_cena", "float"),
                ("datum_kupovine", "polje_datum_kupovine", "text"),
                ("kilometraza_montaze", "polje_kilometraza_montaze", "int"),
                ("napomena", "polje_napomena", "text"),
            ],
            "prikaz": lambda r: f"{r['sezona']} - {r['marka'] or '-'} {r['model'] or '-'} ({r['dimenzija'] or '-'})",
        },
        "registracija": {
            "fields": [
                ("datum_registracije", "polje_datum_registracije", "text"),
                ("istek", "polje_istek", "text"),
                ("cena", "polje_cena", "float"),
                ("tehnicki_pregled", "polje_tehnicki_pregled", "text"),
                ("napomena", "polje_napomena", "text"),
            ],
            "prikaz": lambda r: f"{r['datum_registracije'] or '-'} - istice {r['istek'] or '-'}",
        },
        "osiguranje": {
            "fields": [
                ("vrsta", "polje_vrsta_osiguranja", "text"),
                ("cena", "polje_cena", "float"),
                ("datum", "polje_datum", "text"),
                ("istek", "polje_istek", "text"),
            ],
            "prikaz": lambda r: f"{r['vrsta'] or '-'} - istice {r['istek'] or '-'}",
        },
        "akumulator": {
            "fields": [
                ("marka", "polje_marka", "text"),
                ("model", "polje_model", "text"),
                ("kapacitet", "polje_kapacitet", "text"),
                ("datum_kupovine", "polje_datum_kupovine", "text"),
                ("cena", "polje_cena", "float"),
                ("garancija", "polje_garancija", "text"),
            ],
            "prikaz": lambda r: f"{r['marka'] or '-'} {r['model'] or '-'} - {r['kapacitet'] or '-'}",
        },
        "kvarovi": {
            "fields": [
                ("datum", "polje_datum", "text"),
                ("kilometraza", "polje_kilometraza", "int"),
                ("opis", "polje_opis", "text"),
                ("cena_rada", "polje_cena_rada", "float"),
                ("cena_delova", "polje_cena_delova", "float"),
            ],
            "prikaz": lambda r: (
                f"{r['datum']} - "
                f"{r['ukupna_cena']:.2f} {r['valuta'] or 'RSD'}"
            ),
        },
        "dokumenti": {
            "fields": [
                ("tip", "polje_tip_dokumenta", "text"),
                ("naziv", "polje_naziv", "text"),
                ("putanja", "polje_putanja", "text"),
                ("datum_dodavanja", "polje_datum_dodavanja", "text"),
            ],
            "prikaz": lambda r: f"{r['tip']} - {r['naziv'] or '-'}",
        },
        "podsetnici": {
            "fields": [
                ("tip", "polje_tip_podsetnika", "text"),
                ("naslov", "polje_naslov", "text"),
                ("datum_isteka", "polje_datum_isteka", "text"),
                ("kilometraza_isteka", "polje_kilometraza_isteka", "int"),
            ],
            "prikaz": lambda r: f"{r['naslov'] or r['tip']} - istice {r['datum_isteka'] or '-'}",
        },
    }

    EXTRA_TAB_ICONS = {
        "gume": ("gume.png", "kat_gume"),
        "registracija": ("registracija.png", "kat_registracija"),
        "osiguranje": ("osiguranje.png", "kat_osiguranje"),
        "akumulator": ("akumulator.png", "kat_akumulator"),
        "kvarovi": ("kvarovi.png", "kat_kvarovi"),
        "dokumenti": ("dokumenti.png", "kat_dokumenta"),
        "podsetnici": ("podsetnici.png", "kat_podsetnici"),
        "pdf": ("pdf_izvestaji.png", "kat_pdf"),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._izabrano_vozilo_id = None
        self._vozilo_dugmad = []

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.title_label.text = prevedi("zapisi_naslov", jezik)
        self.ids.tab_products.text = prevedi("kat_gorivo", jezik)
        self.ids.tab_stores.text = prevedi("kat_servisi", jezik)
        self.ids.tab_categories.text = prevedi("kat_troskovi", jezik)
        self.ids.back_btn.text = prevedi("istorija_nazad", jezik)
        self._izabrano_vozilo_id = None
        self._build_extra_tabs()
        self._prikazi_listu_vozila()

    # ---------- Dodatni tabovi (dinamicki, sa ikonicama, u extra_tabs_box) ----------

    def _build_extra_tabs(self):
        jezik = _jezik()
        box = self.ids.extra_tabs_box
        box.clear_widgets()
        assets_dir = App.get_running_app().assets_dir
        for tabela, (icon_fajl, naslov_kljuc) in self.EXTRA_TAB_ICONS.items():
            btn = IconTabButton(
                icon_source=assets_dir + icon_fajl,
                text=prevedi(naslov_kljuc, jezik),
            )
            btn.bind(on_release=lambda inst, t=tabela: self._otvori_kategoriju(t))
            box.add_widget(btn)

    # ---------- Tabovi (nazivi metoda zadrzani zbog kv fajla) ----------

    def show_proizvodi(self):
        self._otvori_kategoriju("gorivo")

    def show_prodavnice(self):
        self._otvori_kategoriju("servisi")

    def show_kategorije(self):
        self._otvori_kategoriju("troskovi")

    def _otvori_kategoriju(self, tabela):
        jezik = _jezik()
        if self._izabrano_vozilo_id is None:
            self._prikazi_kratku_poruku(prevedi("zapisi_prvo_izaberi", jezik))
            return

        vozilo = db.get_by_id("vozila", self._izabrano_vozilo_id)
        if vozilo is None:
            self._izabrano_vozilo_id = None
            self._osvezi_boje_vozila()
            return

        vid = vozilo["id"]
        vnaziv = f"{vozilo['marka']} {vozilo['model']}"

        if tabela == self.PDF_TAB_KEY:
            self._generisi_pdf(vid)
        elif tabela == self.TROSKOVI_TAB_KEY:
            self.open_troskovi_pregled(vid, vnaziv)
        else:
            self.open_records_popup(tabela, vid, vnaziv)

    def _prikazi_kratku_poruku(self, tekst):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(text=tekst, font_size="14sp"))
        popup = Popup(title="", content=content, size_hint=(0.8, 0.3), overlay_color=(0, 0, 0, 0.85))
        close_btn = SecondaryButton(text=prevedi("zapisi_u_redu", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    # ---------- Lista vozila (izbor) ----------

    def _prikazi_listu_vozila(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()
        self._vozilo_dugmad = []

        vozila = db.get_all("vozila", order_by="marka")
        if not vozila:
            box.add_widget(Label(
                text=prevedi("zapisi_nema_vozila", jezik), size_hint_y=None,
                height=dp(40), color=(1, 1, 1, 1),
            ))
            return

        for vozilo in vozila:
            btn = Button(
                text=f"{vozilo['marka']} {vozilo['model']}",
                size_hint_y=None, height=dp(46),
                background_normal="", background_color=BOJA_NEIZABRANO,
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda inst, vid=vozilo["id"]: self._izaberi_vozilo(vid))
            self._vozilo_dugmad.append((vozilo["id"], btn))
            box.add_widget(btn)

        self._osvezi_boje_vozila()

    def _izaberi_vozilo(self, vid):
        self._izabrano_vozilo_id = vid
        self._osvezi_boje_vozila()

    def _osvezi_boje_vozila(self):
        for vid, btn in self._vozilo_dugmad:
            btn.background_color = BOJA_IZABRANO if vid == self._izabrano_vozilo_id else BOJA_NEIZABRANO

    # ---------- PDF izvestaj ----------

    def _podeli_pdf(self, putanja):
        """Otvara standardni Android 'Podeli' meni sa generisanim PDF-om
        (otvori u citacu, posalji na Viber/WhatsApp/mejl, itd). Ako
        uredjaj to ne podrzava, tiho preskace - PDF ostaje sacuvan u
        Download folderu, aplikacija se ne rusi."""
        try:
            from plyer import share
            share.share(
                title="Podeli PDF izvestaj",
                filepath=putanja,
                mimetype="application/pdf",
            )
        except Exception:
            pass

    def _generisi_pdf(self, vehicle_id):
        vozilo = db.get_by_id("vozila", vehicle_id)
        if vozilo is None:
            return

        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
        popup = Popup(
            title=prevedi("kat_pdf", jezik), content=content, size_hint=(0.85, 0.45),
            overlay_color=(0, 0, 0, 0.85),
        )

        try:
            putanja = pdf_report.generisi_pdf_izvestaj(vozilo)
            poruka = "PDF je generisan i sacuvan u Download folderu."
            self._podeli_pdf(putanja)
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

        close_btn = SecondaryButton(text=prevedi("zapisi_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    # ---------- Troskovi: pregled po periodu, sa rucnim prebacivanjem prikazne valute ----------

    def _prikazi_zbir_u_box(self, box, naslov, zbir, prikaz_valuta, jezik):
        box.add_widget(Label(
            text=naslov, bold=True, font_size="15sp",
            size_hint_y=None, height=dp(26),
        ))
        for kljuc, label_kljuc in KATEGORIJE_TROSKOVA:
            box.add_widget(Label(
                text=f"{prevedi(label_kljuc, jezik)}: {zbir[kljuc]:.2f} {prikaz_valuta}",
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
        jezik = _jezik()
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
            title=prevedi("kat_troskovi", jezik), content=content, size_hint=(0.94, 0.9),
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
            self._prikazi_zbir_u_box(inner, "Ova nedelja", zbir_nedelja, pv, jezik)

            pocetak_meseca = danas.replace(day=1, hour=0, minute=0, second=0)
            poslednji_dan_meseca = calendar.monthrange(danas.year, danas.month)[1]
            kraj_meseca = danas.replace(day=poslednji_dan_meseca, hour=23, minute=59, second=59)
            zbir_mesec = db.troskovi_pregled(vehicle_id, pocetak_meseca, kraj_meseca, pv)
            self._prikazi_zbir_u_box(inner, "Ovaj mesec", zbir_mesec, pv, jezik)

            pocetak_godine = danas.replace(month=1, day=1, hour=0, minute=0, second=0)
            kraj_godine = danas.replace(month=12, day=31, hour=23, minute=59, second=59)
            zbir_godina = db.troskovi_pregled(vehicle_id, pocetak_godine, kraj_godine, pv)
            self._prikazi_zbir_u_box(inner, "Ova godina", zbir_godina, pv, jezik)

            if izabrani_period["tip"] == "mesec":
                g, m = izabrani_period["godina"], izabrani_period["mesec"]
                prvi = datetime(g, m, 1)
                poslednji_dan = calendar.monthrange(g, m)[1]
                poslednji = datetime(g, m, poslednji_dan, 23, 59, 59)
                naziv_meseca = prvi.strftime("%B %Y")
                zbir = db.troskovi_pregled(vehicle_id, prvi, poslednji, pv)
                self._prikazi_zbir_u_box(inner, f"Izabrano: {naziv_meseca}", zbir, pv, jezik)
            elif izabrani_period["tip"] == "godina":
                g = izabrani_period["godina"]
                prvi = datetime(g, 1, 1)
                poslednji = datetime(g, 12, 31, 23, 59, 59)
                zbir = db.troskovi_pregled(vehicle_id, prvi, poslednji, pv)
                self._prikazi_zbir_u_box(inner, f"Izabrano: godina {g}", zbir, pv, jezik)

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

        close_btn = SecondaryButton(text=prevedi("zapisi_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        iscrtaj_sve()
        popup.open()

    # ---------- Zapisi jednog vozila (za dati tab) ----------

    def open_records_popup(self, tabela, vehicle_id, vozilo_naziv):
        jezik = _jezik()
        naslov_kljuc = NASLOVI[tabela]
        naslov_teksta = prevedi(naslov_kljuc, jezik)
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        content.add_widget(Label(
            text=f"{vozilo_naziv} - {naslov_teksta}", bold=True, font_size="18sp",
            size_hint_y=None, height=dp(32),
        ))

        records_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        records_box.bind(minimum_height=records_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(records_box)
        content.add_widget(scroll)

        popup = Popup(
            title=naslov_teksta, content=content, size_hint=(0.94, 0.85),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            records_box.clear_widgets()
            tab_def = self.TAB_DEFS[tabela]
            zapisi = db.get_by_vehicle(tabela, vehicle_id, order_by="id DESC")
            if not zapisi:
                records_box.add_widget(Label(
                    text=prevedi("zapisi_nema_zapisa", jezik), size_hint_y=None,
                    height=dp(36), color=(0.75, 0.75, 0.75, 1),
                ))
            for red in zapisi:
                btn = SecondaryButton(
                    text=tab_def["prikaz"](red), size_hint_y=None, height=dp(52),
                )
                if tabela == "dokumenti":
                    btn.bind(
                        on_release=lambda inst, rid=red["id"]:
                            self.open_view_dokument_popup(rid, vehicle_id, refresh)
                    )
                else:
                    btn.bind(
                        on_release=lambda inst, rid=red["id"]:
                            self.open_edit_record_popup(tabela, rid, vehicle_id, popup, refresh)
                    )
                records_box.add_widget(btn)

        novi_btn = PrimaryButton(text=prevedi("zapisi_dodaj_zapis", jezik), size_hint_y=None, height=dp(44))
        if tabela == "dokumenti":
            novi_btn.bind(
                on_release=lambda inst: self.open_add_dokument_popup(vehicle_id, popup, refresh)
            )
        else:
            novi_btn.bind(
                on_release=lambda inst: self.open_add_record_popup(tabela, vehicle_id, popup, refresh)
            )
        content.add_widget(novi_btn)

        if tabela == "gorivo":
            pumpe_btn = SecondaryButton(text="Pregled po pumpama", size_hint_y=None, height=dp(44))
            pumpe_btn.bind(on_release=lambda inst: self.open_pregled_po_pumpama(vehicle_id, vozilo_naziv))
            content.add_widget(pumpe_btn)

        close_btn = SecondaryButton(text=prevedi("zapisi_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    # ---------- Gorivo: pregled po pumpama (nedelja/mesec/godina) ----------

    def open_pregled_po_pumpama(self, vehicle_id, vozilo_naziv):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(
            text=f"{vozilo_naziv} - Gorivo po pumpama", bold=True, font_size="16sp",
            size_hint_y=None, height=dp(30),
        ))

        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        inner.bind(minimum_height=inner.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(inner)
        content.add_widget(scroll)

        popup = Popup(
            title="Pregled po pumpama", content=content, size_hint=(0.94, 0.9),
            overlay_color=(0, 0, 0, 0.85),
        )

        def prikazi_period(naslov, od, do):
            inner.add_widget(Label(
                text=naslov, bold=True, font_size="15sp",
                size_hint_y=None, height=dp(28),
            ))
            po_pumpi = db.gorivo_po_pumpama(vehicle_id, od, do)
            if not po_pumpi:
                inner.add_widget(Label(
                    text="Nema zapisa.", size_hint_y=None, height=dp(22),
                    color=(0.75, 0.75, 0.75, 1), font_size="12sp",
                ))
            ukupno = 0.0
            for naziv, vrednosti in sorted(po_pumpi.items()):
                inner.add_widget(Label(
                    text=f"{naziv}: {vrednosti['litara']:.2f} L - {vrednosti['ukupno']:.2f} RSD",
                    size_hint_y=None, height=dp(22), font_size="13sp",
                ))
                ukupno += vrednosti["ukupno"]
            inner.add_widget(Label(
                text=f"UKUPNO: {ukupno:.2f} RSD",
                bold=True, size_hint_y=None, height=dp(26),
                color=(0.6, 0.85, 1, 1), font_size="14sp",
            ))
            inner.add_widget(Label(text="", size_hint_y=None, height=dp(10)))

        danas = datetime.now()

        pocetak_nedelje = danas - timedelta(days=danas.weekday())
        pocetak_nedelje = pocetak_nedelje.replace(hour=0, minute=0, second=0)
        kraj_nedelje = pocetak_nedelje + timedelta(days=6, hours=23, minutes=59, seconds=59)
        prikazi_period("Ova nedelja", pocetak_nedelje, kraj_nedelje)

        pocetak_meseca = danas.replace(day=1, hour=0, minute=0, second=0)
        poslednji_dan_meseca = calendar.monthrange(danas.year, danas.month)[1]
        kraj_meseca = danas.replace(day=poslednji_dan_meseca, hour=23, minute=59, second=59)
        prikazi_period("Ovaj mesec", pocetak_meseca, kraj_meseca)

        pocetak_godine = danas.replace(month=1, day=1, hour=0, minute=0, second=0)
        kraj_godine = danas.replace(month=12, day=31, hour=23, minute=59, second=59)
        prikazi_period("Ova godina", pocetak_godine, kraj_godine)

        close_btn = SecondaryButton(text=prevedi("zapisi_zatvori", _jezik()), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    # ---------- Dodavanje / izmena zapisa ----------

    def _build_form(self, tabela, existing=None, valuta_stanje=None):
        jezik = _jezik()
        tab_def = self.TAB_DEFS[tabela]
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        if tabela in TABELE_SA_VALUTOM:
            pocetna_valuta = "RSD"
            if existing is not None and existing["valuta"]:
                pocetna_valuta = existing["valuta"]
            valuta_stanje["valuta"] = pocetna_valuta

            valuta_btn = PrimaryButton(
                text=f"{prevedi('polje_valuta', jezik)}: {pocetna_valuta}", size_hint_y=None, height=dp(44),
            )

            def promeni_valutu(*a):
                valuta_stanje["valuta"] = "EUR" if valuta_stanje["valuta"] == "RSD" else "RSD"
                valuta_btn.text = f"{prevedi('polje_valuta', jezik)}: {valuta_stanje['valuta']}"

            valuta_btn.bind(on_release=promeni_valutu)
            content.add_widget(valuta_btn)

        inputs = {}
        for key, label_kljuc, tip in tab_def["fields"]:
            vrednost = ""
            if existing is not None and existing[key] is not None:
                vrednost = str(existing[key])
            tf = StyledTextInput(
                text=vrednost, hint_text=prevedi(label_kljuc, jezik),
                input_filter=("float" if tip == "float" else "int" if tip == "int" else None),
                multiline=False, size_hint_y=None, height=dp(44),
            )
            inputs[key] = tf
            content.add_widget(tf)

        return content, inputs

    def _collect_data(self, tabela, inputs, valuta_stanje=None):
        tab_def = self.TAB_DEFS[tabela]
        data = {}
        for key, _label_kljuc, tip in tab_def["fields"]:
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

    def _ocr_api_kljuc(self):
        return db.get_setting("ocr_api_key", "")

    def _trazi_ocr_kljuc(self, posle_unosa):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(
            text="Unesi OCR.space API kljuc (samo prvi put):",
            size_hint_y=None, height=dp(40),
        ))
        kljuc_input = StyledTextInput(multiline=False, size_hint_y=None, height=dp(44))
        content.add_widget(kljuc_input)
        popup = Popup(
            title="OCR API kljuc", content=content, size_hint=(0.9, 0.4),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def sacuvaj(*a):
            vrednost = kljuc_input.text.strip()
            if vrednost:
                db.set_setting("ocr_api_key", vrednost)
            popup.dismiss()
            posle_unosa(vrednost)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=sacuvaj)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=lambda *a: (popup.dismiss(), posle_unosa(None)))
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup.open()

    def open_add_record_popup(self, tabela, vehicle_id, parent_popup, refresh_parent):
        jezik = _jezik()
        valuta_stanje = {}
        content, inputs = self._build_form(tabela, valuta_stanje=valuta_stanje)
        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        scroll_wrap = ScrollView(size_hint=(1, None), height=dp(400))
        scroll_wrap.add_widget(content)
        outer = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        if tabela == "gorivo":
            def pokreni_ocr(kljuc):
                def obradi_u_pozadini(putanja):
                    try:
                        podaci = ocr_racun.ocitaj_racun(putanja, kljuc)
                        greska = None
                    except Exception as e:
                        podaci = None
                        greska = str(e)
                    Clock.schedule_once(lambda dt: primeni_rezultat(podaci, greska), 0)

                def primeni_rezultat(podaci, greska):
                    if greska:
                        error_label.text = f"OCR greska: {greska}"
                        return
                    if podaci.get("pumpa"):
                        inputs["pumpa"].text = podaci["pumpa"]
                    if podaci.get("litara"):
                        inputs["litara"].text = str(podaci["litara"])
                    if podaci.get("cena_po_litru"):
                        inputs["cena_po_litru"].text = str(podaci["cena_po_litru"])
                    if podaci.get("datum"):
                        inputs["datum"].text = podaci["datum"]
                    error_label.text = "Racun ucitan - proveri podatke pre cuvanja."

                def na_izboru(izbor):
                    if not izbor:
                        return
                    error_label.text = "Ucitavam racun..."
                    threading.Thread(
                        target=obradi_u_pozadini, args=(str(izbor[0]),), daemon=True,
                    ).start()

                try:
                    from plyer import filechooser
                    filechooser.open_file(
                        on_selection=na_izboru,
                        filters=[["Images", "*.jpg", "*.jpeg", "*.png"]],
                    )
                except Exception as e:
                    error_label.text = f"Ne mogu da otvorim galeriju: {e}"

            def skeniraj_racun(*a):
                kljuc = self._ocr_api_kljuc()
                if not kljuc:
                    self._trazi_ocr_kljuc(lambda novi: novi and pokreni_ocr(novi))
                    return
                pokreni_ocr(kljuc)

            ocr_btn = PrimaryButton(text="Skeniraj racun (OCR)", size_hint_y=None, height=dp(48))
            ocr_btn.bind(on_release=skeniraj_racun)
            outer.add_widget(ocr_btn)

        outer.add_widget(scroll_wrap)

        popup = Popup(
            title=prevedi("zapisi_novi_zapis", jezik), content=outer, size_hint=(0.9, 0.85),
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
        save_btn = PrimaryButton(text=prevedi("zapisi_sacuvaj", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("zapisi_otkazi", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        outer.add_widget(btn_row)

        popup.open()

    def open_edit_record_popup(self, tabela, record_id, vehicle_id, parent_popup, refresh_parent):
        jezik = _jezik()
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
            title=prevedi("zapisi_izmeni_zapis", jezik), content=outer, size_hint=(0.9, 0.85),
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
                instance.text = prevedi("zapisi_potvrdi_brisanje", jezik)
                return
            db.delete(tabela, record_id)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("zapisi_sacuvaj", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("zapisi_otkazi", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        outer.add_widget(btn_row)

        delete_btn = DangerButton(text=prevedi("zapisi_obrisi_zapis", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        outer.add_widget(delete_btn)

        popup.open()

    # ---------- Dokumenta: slikanje i pregled slike ----------

    def open_add_dokument_popup(self, vehicle_id, parent_popup, refresh_parent):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        tip_input = StyledTextInput(
            hint_text=prevedi("polje_tip_dokumenta", jezik),
            multiline=False, size_hint_y=None, height=dp(44),
        )
        naziv_input = StyledTextInput(
            hint_text=prevedi("polje_naziv", jezik),
            multiline=False, size_hint_y=None, height=dp(44),
        )
        content.add_widget(tip_input)
        content.add_widget(naziv_input)

        from camera4kivy import Preview
        preview = Preview(size_hint_y=1)
        content.add_widget(preview)

        status_label = Label(
            text=prevedi("dokumenti_nema_slike", jezik), size_hint_y=None,
            height=dp(40), color=(0.75, 0.75, 0.75, 1),
            halign="left", valign="middle",
        )
        status_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        content.add_widget(status_label)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        slika_stanje = {"putanja": None, "cekanje_event": None}

        def _pronadji_snimljenu_sliku(naziv_bez_ekstenzije):
            try:
                from android.storage import primary_external_storage_path
                dcim = os.path.join(primary_external_storage_path(), "DCIM")
            except ImportError:
                dcim = None
            if dcim and os.path.isdir(dcim):
                for koren, _dirs, fajlovi in os.walk(dcim):
                    for f in fajlovi:
                        if f.startswith(naziv_bez_ekstenzije):
                            return os.path.join(koren, f)
            return None

        def slika_snimljena(putanja):
            if slika_stanje["cekanje_event"]:
                slika_stanje["cekanje_event"].cancel()
                slika_stanje["cekanje_event"] = None
            if not putanja:
                status_label.text = prevedi("dokumenti_greska_slikanja", jezik)
                return
            slika_stanje["putanja"] = putanja
            status_label.text = prevedi("dokumenti_slika_snimljena", jezik)

        def potrazi_na_disku(naziv, pokusaji_ostalo, dt):
            pronadjeno = _pronadji_snimljenu_sliku(naziv)
            if pronadjeno:
                slika_snimljena(pronadjeno)
                return
            if pokusaji_ostalo <= 0:
                status_label.text = "Slika nije pronadjena na disku (proveri Galeriju rucno)."
                return
            slika_stanje["cekanje_event"] = Clock.schedule_once(
                lambda dt2: potrazi_na_disku(naziv, pokusaji_ostalo - 1, dt2), 1
            )

        def slikaj(*a):
            status_label.text = "Snimam..."
            naziv_fajla = f"dok_{int(time.time())}"
            try:
                preview.capture_photo(subdir="dokumenti_slike", name=naziv_fajla)
            except Exception as e:
                status_label.text = f"{prevedi('dokumenti_greska_slikanja', jezik)} ({e})"
                return
            slika_stanje["cekanje_event"] = Clock.schedule_once(
                lambda dt: potrazi_na_disku(naziv_fajla, 8, dt), 1
            )

        slikaj_btn = PrimaryButton(text=prevedi("dokumenti_slikaj_btn", jezik), size_hint_y=None, height=dp(48))
        slikaj_btn.bind(on_release=slikaj)
        content.add_widget(slikaj_btn)

        def proveri_konekciju(dt):
            povezano = getattr(preview, "camera_connected", False)
            status_label.text = f"Kamera povezana: {povezano}"
            if povezano:
                return False

        Clock.schedule_interval(proveri_konekciju, 1)

        popup = Popup(
            title=prevedi("zapisi_novi_zapis", jezik), content=content, size_hint=(0.95, 0.95),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def na_otvaranje(*a):
            try:
                preview.connect_camera(filepath_callback=slika_snimljena, enable_video=False)
            except Exception as e:
                status_label.text = f"{prevedi('dokumenti_kamera_nedostupna', jezik)} ({e})"

        def na_zatvaranje(*a):
            try:
                preview.disconnect_camera()
            except Exception:
                pass

        popup.bind(on_open=na_otvaranje, on_dismiss=na_zatvaranje)

        def save(*a):
            if not naziv_input.text.strip():
                error_label.text = prevedi("dokumenti_greska_naziv", jezik)
                return
            if not slika_stanje["putanja"]:
                error_label.text = prevedi("dokumenti_greska_slika", jezik)
                return
            data = {
                "tip": tip_input.text.strip(),
                "naziv": naziv_input.text.strip(),
                "putanja": slika_stanje["putanja"],
                "datum_dodavanja": datetime.now().strftime("%d.%m.%Y"),
                "vehicle_id": vehicle_id,
            }
            db.insert("dokumenti", data)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("zapisi_sacuvaj", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("zapisi_otkazi", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup.open()

    def open_view_dokument_popup(self, record_id, vehicle_id, refresh_parent):
        jezik = _jezik()
        red = db.get_by_id("dokumenti", record_id)
        if red is None:
            return

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(
            text=red["naziv"] or "-", bold=True, font_size="16sp",
            size_hint_y=None, height=dp(28),
        ))

        img = KivyImage(
            source=red["putanja"] or "", allow_stretch=True, keep_ratio=True, size_hint_y=1,
        )
        content.add_widget(img)

        popup = Popup(
            title=red["tip"] or "", content=content, size_hint=(0.94, 0.9),
            overlay_color=(0, 0, 0, 0.85),
        )

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("zapisi_potvrdi_brisanje", jezik)
                return
            db.delete("dokumenti", record_id)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        delete_btn = DangerButton(text=prevedi("zapisi_obrisi_zapis", jezik))
        delete_btn.bind(on_release=delete)
        close_btn = SecondaryButton(text=prevedi("zapisi_zatvori", jezik))
        close_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(delete_btn)
        btn_row.add_widget(close_btn)
        content.add_widget(btn_row)

        popup.open()

    def go_back(self):
        self.manager.current = "home"

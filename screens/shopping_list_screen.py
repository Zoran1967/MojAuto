from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput, Card
from database import db
from translations import prevedi


def _jezik():
    return db.get_setting("jezik", "sr")


class ShoppingListScreen(Screen):
    """
    Ekran za pregled i upravljanje vozilima (prepravljen iz Shopping
    List ekrana - naziv fajla/klase i ids su namerno zadrzani da se ne
    bi diralo main.py ni kv fajl u istoj izmeni).

    Napomena o valuti: kupovna_cena bira svoju valutu (RSD ili EUR)
    prilikom unosa - cuva se uz vozilo, prikazuje se bez konverzije.
    Tekstovi se prevode preko translations.prevedi() prema trenutno
    izabranom jeziku.
    """

    FIELD_DEFS = [
        ("marka", "polje_marka", "text"),
        ("model", "polje_model", "text"),
        ("godina", "polje_godina", "int"),
        ("registracija", "polje_registracija", "text"),
        ("vin", "polje_vin", "text"),
        ("broj_sasije", "polje_broj_sasije", "text"),
        ("broj_motora", "polje_broj_motora", "text"),
        ("gorivo", "polje_gorivo", "text"),
        ("zapremina", "polje_zapremina", "float"),
        ("snaga", "polje_snaga", "int"),
        ("menjac", "polje_menjac", "text"),
        ("boja", "polje_boja", "text"),
        ("broj_vrata", "polje_broj_vrata", "int"),
        ("datum_kupovine", "polje_datum_kupovine", "text"),
        ("kupovna_cena", "polje_kupovna_cena", "float"),
        ("kilometraza", "polje_kilometraza", "int"),
        ("napomena", "polje_napomena", "text"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selektovano_vozilo_id = None

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.add_product_btn.text = prevedi("vozila_dodaj_btn", jezik)
        self.ids.grand_total_word.text = prevedi("vozila_ukupno", jezik)
        self.ids.back_btn.text = prevedi("istorija_nazad", jezik)
        self.load_open_lists()

    # ---------- Prikaz liste vozila ----------

    def load_open_lists(self):
        jezik = _jezik()
        box = self.ids.items_box
        box.clear_widgets()

        vozila = db.get_all("vozila", order_by="marka")

        if not vozila:
            box.add_widget(Label(
                text=prevedi("vozila_nema", jezik),
                size_hint_y=None, height=dp(60), color=(0.75, 0.75, 0.75, 1),
            ))
        else:
            for vozilo in vozila:
                self._napravi_karticu_vozila(box, vozilo)

        self.ids.grand_total_label.text = str(len(vozila))

    def _napravi_karticu_vozila(self, parent_box, vozilo):
        jezik = _jezik()
        card = Card(orientation="vertical", padding=dp(10), spacing=dp(6),
                    size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))

        header = Label(
            text=f"{vozilo['marka']} {vozilo['model']} ({vozilo['godina'] or '-'})",
            bold=True, font_size="16sp",
            size_hint_y=None, height=dp(28),
        )
        card.add_widget(header)

        info = Label(
            text=f"{prevedi('polje_registracija', jezik)}: {vozilo['registracija'] or '-'}   {prevedi('polje_kilometraza', jezik)}: {vozilo['kilometraza']} km",
            font_size="13sp", size_hint_y=None, height=dp(24),
        )
        card.add_widget(info)

        if vozilo["kupovna_cena"] not in (None, 0):
            valuta = vozilo["valuta"] or "RSD"
            cena_label = Label(
                text=f"{prevedi('polje_kupovna_cena', jezik)}: {vozilo['kupovna_cena']:.2f} {valuta}",
                font_size="13sp", size_hint_y=None, height=dp(24),
                color=(0.6, 0.85, 1, 1),
            )
            card.add_widget(cena_label)

        izmeni_btn = Button(
            text=prevedi("vozila_izmeni_btn", jezik),
            size_hint_y=None, height=dp(40),
            background_normal="", background_color=(0.20, 0.20, 0.22, 1),
            color=(1, 1, 1, 1), font_size="13sp",
        )
        izmeni_btn.bind(on_release=lambda inst, vid=vozilo["id"]: self.open_edit_item_popup(vid))
        card.add_widget(izmeni_btn)

        parent_box.add_widget(card)

    # ---------- Zajednicka forma (dodavanje i izmena) ----------

    def _build_form(self, existing=None, valuta_stanje=None):
        jezik = _jezik()
        inner = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10), size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))

        pocetna_valuta = "RSD"
        if existing is not None and existing["valuta"]:
            pocetna_valuta = existing["valuta"]
        valuta_stanje["valuta"] = pocetna_valuta

        valuta_btn = PrimaryButton(
            text=f"{prevedi('polje_valuta_kupovina', jezik)}: {pocetna_valuta}",
            size_hint_y=None, height=dp(44),
        )

        def promeni_valutu(*a):
            valuta_stanje["valuta"] = "EUR" if valuta_stanje["valuta"] == "RSD" else "RSD"
            valuta_btn.text = f"{prevedi('polje_valuta_kupovina', jezik)}: {valuta_stanje['valuta']}"

        valuta_btn.bind(on_release=promeni_valutu)
        inner.add_widget(valuta_btn)

        inputs = {}
        for key, label_kljuc, tip in self.FIELD_DEFS:
            vrednost = ""
            if existing is not None and existing[key] is not None:
                vrednost = str(existing[key])
            tf = StyledTextInput(
                text=vrednost, hint_text=prevedi(label_kljuc, jezik),
                input_filter=("float" if tip == "float" else "int" if tip == "int" else None),
                multiline=False, size_hint_y=None, height=dp(44),
            )
            inputs[key] = tf
            inner.add_widget(tf)

        scroll = ScrollView(size_hint=(1, None), height=dp(420))
        scroll.add_widget(inner)
        return scroll, inputs

    def _collect_data(self, inputs, valuta_stanje):
        int_fields = {"godina", "snaga", "kilometraza", "broj_vrata"}
        float_fields = {"zapremina", "kupovna_cena"}
        data = {}
        for key, _label_kljuc, _tip in self.FIELD_DEFS:
            tekst = inputs[key].text.strip()
            if key in int_fields:
                data[key] = int(tekst) if tekst else (0 if key == "kilometraza" else None)
            elif key in float_fields:
                data[key] = float(tekst.replace(",", ".")) if tekst else None
            else:
                data[key] = tekst
        data["valuta"] = valuta_stanje["valuta"]
        return data

    # ---------- Dodavanje vozila ----------

    def add_item(self):
        self.open_add_item_popup()

    def open_add_item_popup(self):
        jezik = _jezik()
        valuta_stanje = {}
        scroll, inputs = self._build_form(valuta_stanje=valuta_stanje)

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("vozila_dodaj_naslov", jezik), content=content, size_hint=(0.92, 0.9),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def confirm(*a):
            data = self._collect_data(inputs, valuta_stanje)
            if not data.get("marka") or not data.get("model"):
                error_label.text = prevedi("vozila_greska_obavezno", jezik)
                return
            db.insert("vozila", data)
            popup.dismiss()
            self.load_open_lists()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text=prevedi("vozila_sacuvaj", jezik))
        add_btn.bind(on_release=confirm)
        cancel_btn = SecondaryButton(text=prevedi("vozila_otkazi", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup.open()

    # ---------- Izmena / brisanje vozila ----------

    def open_edit_item_popup(self, vozilo_id):
        jezik = _jezik()
        vozilo = db.get_by_id("vozila", vozilo_id)
        if vozilo is None:
            return

        valuta_stanje = {}
        scroll, inputs = self._build_form(existing=vozilo, valuta_stanje=valuta_stanje)

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("vozila_izmeni_naslov", jezik), content=content, size_hint=(0.92, 0.9),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            data = self._collect_data(inputs, valuta_stanje)
            if not data.get("marka") or not data.get("model"):
                error_label.text = prevedi("vozila_greska_obavezno", jezik)
                return
            db.update("vozila", vozilo_id, data)
            popup.dismiss()
            self.load_open_lists()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("vozila_potvrdi_brisanje", jezik)
                return
            db.delete("vozila", vozilo_id)
            popup.dismiss()
            self.load_open_lists()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("vozila_sacuvaj", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("vozila_otkazi", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text=prevedi("vozila_obrisi_btn", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    # ---------- Navigacija ----------

    def go_back(self):
        self.manager.current = "home"

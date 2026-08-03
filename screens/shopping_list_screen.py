from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput, Card
from database import db


class ShoppingListScreen(Screen):
    """
    Ekran za pregled i upravljanje vozilima (prepravljen iz Shopping
    List ekrana - naziv fajla/klase i ids su namerno zadrzani da se ne
    bi diralo main.py ni kv fajl u istoj izmeni).
    """

    FIELD_DEFS = [
        ("marka", "Marka", "text"),
        ("model", "Model", "text"),
        ("godina", "Godina", "int"),
        ("registracija", "Registracija", "text"),
        ("vin", "VIN", "text"),
        ("broj_sasije", "Broj sasije", "text"),
        ("broj_motora", "Broj motora", "text"),
        ("gorivo", "Gorivo", "text"),
        ("zapremina", "Zapremina (L)", "float"),
        ("snaga", "Snaga (KS)", "int"),
        ("menjac", "Menjac", "text"),
        ("boja", "Boja", "text"),
        ("datum_kupovine", "Datum kupovine (DD.MM.GGGG)", "text"),
        ("kupovna_cena", "Kupovna cena", "float"),
        ("kilometraza", "Kilometraza", "int"),
        ("napomena", "Napomena", "text"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selektovano_vozilo_id = None

    def on_pre_enter(self, *args):
        self.ids.add_product_btn.text = "+ Dodaj vozilo"
        self.ids.grand_total_word.text = "UKUPNO VOZILA:"
        self.load_open_lists()

    # ---------- Prikaz liste vozila ----------

    def load_open_lists(self):
        box = self.ids.items_box
        box.clear_widgets()

        vozila = db.get_all("vozila", order_by="marka")

        if not vozila:
            box.add_widget(Label(
                text="Nema dodatih vozila.",
                size_hint_y=None, height=dp(60), color=(0.75, 0.75, 0.75, 1),
            ))
        else:
            for vozilo in vozila:
                self._napravi_karticu_vozila(box, vozilo)

        self.ids.grand_total_label.text = str(len(vozila))

    def _napravi_karticu_vozila(self, parent_box, vozilo):
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
            text=f"Registracija: {vozilo['registracija'] or '-'}   Kilometraza: {vozilo['kilometraza']} km",
            font_size="13sp", size_hint_y=None, height=dp(24),
        )
        card.add_widget(info)

        izmeni_btn = Button(
            text="Izmeni / Obrisi",
            size_hint_y=None, height=dp(40),
            background_normal="", background_color=(0.20, 0.20, 0.22, 1),
            color=(1, 1, 1, 1), font_size="13sp",
        )
        izmeni_btn.bind(on_release=lambda inst, vid=vozilo["id"]: self.open_edit_item_popup(vid))
        card.add_widget(izmeni_btn)

        parent_box.add_widget(card)

    # ---------- Zajednicka forma (dodavanje i izmena) ----------

    def _build_form(self, existing=None):
        inner = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10), size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))

        inputs = {}
        for key, label, tip in self.FIELD_DEFS:
            vrednost = ""
            if existing is not None and existing[key] is not None:
                vrednost = str(existing[key])
            tf = StyledTextInput(
                text=vrednost, hint_text=label,
                input_filter=("float" if tip == "float" else "int" if tip == "int" else None),
                multiline=False, size_hint_y=None, height=dp(44),
            )
            inputs[key] = tf
            inner.add_widget(tf)

        scroll = ScrollView(size_hint=(1, None), height=dp(420))
        scroll.add_widget(inner)
        return scroll, inputs

    def _collect_data(self, inputs):
        int_fields = {"godina", "snaga", "kilometraza"}
        float_fields = {"zapremina", "kupovna_cena"}
        data = {}
        for key, _label, _tip in self.FIELD_DEFS:
            tekst = inputs[key].text.strip()
            if key in int_fields:
                data[key] = int(tekst) if tekst else (0 if key == "kilometraza" else None)
            elif key in float_fields:
                data[key] = float(tekst.replace(",", ".")) if tekst else None
            else:
                data[key] = tekst
        return data

    # ---------- Dodavanje vozila ----------

    def add_item(self):
        self.open_add_item_popup()

    def open_add_item_popup(self):
        scroll, inputs = self._build_form()

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title="Dodaj vozilo", content=content, size_hint=(0.92, 0.9),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def confirm(*a):
            data = self._collect_data(inputs)
            if not data.get("marka") or not data.get("model"):
                error_label.text = "Marka i model su obavezni."
                return
            db.insert("vozila", data)
            popup.dismiss()
            self.load_open_lists()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text="Sacuvaj")
        add_btn.bind(on_release=confirm)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup.open()

    # ---------- Izmena / brisanje vozila ----------

    def open_edit_item_popup(self, vozilo_id):
        vozilo = db.get_by_id("vozila", vozilo_id)
        if vozilo is None:
            return

        scroll, inputs = self._build_form(existing=vozilo)

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title="Izmeni vozilo", content=content, size_hint=(0.92, 0.9),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            data = self._collect_data(inputs)
            if not data.get("marka") or not data.get("model"):
                error_label.text = "Marka i model su obavezni."
                return
            db.update("vozila", vozilo_id, data)
            popup.dismiss()
            self.load_open_lists()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = "Potvrdi brisanje"
                return
            db.delete("vozila", vozilo_id)
            popup.dismiss()
            self.load_open_lists()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text="Obrisi vozilo", size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    # ---------- Navigacija ----------

    def go_back(self):
        self.manager.current = "home"

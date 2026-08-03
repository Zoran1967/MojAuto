from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp

from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput, Card
from database import db


class ShoppingListScreen(Screen):
    """
    Ekran za pregled i upravljanje vozilima (prepravljen iz Shopping
    List ekrana - naziv fajla/klase i ids su namerno zadrzani da se ne
    bi diralo main.py ni kv fajl u istoj izmeni).
    """

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

    # ---------- Dodavanje vozila ----------

    def add_item(self):
        self.open_add_item_popup()

    def open_add_item_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        marka_input = StyledTextInput(hint_text="Marka", size_hint_y=None, height=dp(44), multiline=False)
        model_input = StyledTextInput(hint_text="Model", size_hint_y=None, height=dp(44), multiline=False)
        godina_input = StyledTextInput(hint_text="Godina", input_filter="int", size_hint_y=None, height=dp(44), multiline=False)
        registracija_input = StyledTextInput(hint_text="Registracija", size_hint_y=None, height=dp(44), multiline=False)
        kilometraza_input = StyledTextInput(hint_text="Kilometraza", input_filter="int", size_hint_y=None, height=dp(44), multiline=False)

        for w in (marka_input, model_input, godina_input, registracija_input, kilometraza_input):
            content.add_widget(w)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title="Dodaj vozilo", content=content, size_hint=(0.9, 0.7),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def confirm(*a):
            marka = marka_input.text.strip()
            model = model_input.text.strip()
            if not marka or not model:
                error_label.text = "Marka i model su obavezni."
                return
            db.insert("vozila", {
                "marka": marka,
                "model": model,
                "godina": int(godina_input.text) if godina_input.text.strip() else None,
                "registracija": registracija_input.text.strip(),
                "kilometraza": int(kilometraza_input.text) if kilometraza_input.text.strip() else 0,
            })
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

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        marka_input = StyledTextInput(text=vozilo["marka"] or "", size_hint_y=None, height=dp(44), multiline=False)
        model_input = StyledTextInput(text=vozilo["model"] or "", size_hint_y=None, height=dp(44), multiline=False)
        godina_input = StyledTextInput(
            text=str(vozilo["godina"]) if vozilo["godina"] else "",
            input_filter="int", size_hint_y=None, height=dp(44), multiline=False,
        )
        registracija_input = StyledTextInput(text=vozilo["registracija"] or "", size_hint_y=None, height=dp(44), multiline=False)
        kilometraza_input = StyledTextInput(
            text=str(vozilo["kilometraza"]) if vozilo["kilometraza"] else "0",
            input_filter="int", size_hint_y=None, height=dp(44), multiline=False,
        )

        for w in (marka_input, model_input, godina_input, registracija_input, kilometraza_input):
            content.add_widget(w)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title="Izmeni vozilo", content=content, size_hint=(0.9, 0.75),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            marka = marka_input.text.strip()
            model = model_input.text.strip()
            if not marka or not model:
                error_label.text = "Marka i model su obavezni."
                return
            db.update("vozila", vozilo_id, {
                "marka": marka,
                "model": model,
                "godina": int(godina_input.text) if godina_input.text.strip() else None,
                "registracija": registracija_input.text.strip(),
                "kilometraza": int(kilometraza_input.text) if kilometraza_input.text.strip() else 0,
            })
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

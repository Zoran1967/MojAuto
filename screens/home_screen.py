from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import StringProperty

from database import db
from widgets import PrimaryButton, SecondaryButton


class HomeScreen(Screen):
    """
    Pocetni ekran: dugmad za Vozila, Istoriju, Zapise (gorivo/servisi/troskovi)
    i Podesavanja, plus dugme za izbor jezika (globus).
    """

    JEZICI = [
        ("sr", "Srpski"),
        ("en", "English"),
        ("de", "Deutsch"),
        ("sk", "Slovencina"),
        ("uk", "Українська"),
        ("it", "Italiano"),
        ("fr", "Francais"),
        ("bg", "Български"),
    ]

    txt_new_list = StringProperty("Vozila")
    txt_history = StringProperty("Istorija")
    txt_database = StringProperty("Zapisi")
    txt_settings = StringProperty("Podesavanja")

    def on_pre_enter(self, *args):
        pass

    def go_to_new_list(self):
        self.manager.current = "shopping_list"

    def go_to_history(self):
        self.manager.current = "history"

    def go_to_database(self):
        self.manager.current = "database"

    def go_to_settings(self):
        self.manager.current = "settings"

    # ---------- Izbor jezika ----------

    def open_language_picker(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        popup = Popup(
            title="Izaberi jezik / Select language",
            content=content, size_hint=(0.85, 0.75),
            overlay_color=(0, 0, 0, 0.85),
        )

        trenutni = db.get_setting("jezik", "sr")
        for kod, naziv in self.JEZICI:
            is_current = kod == trenutni
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv} (aktivan)" if is_current else naziv),
                size_hint_y=None, height=dp(48),
            )
            btn.bind(on_release=lambda inst, k=kod: self.choose_language(k, popup))
            box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    def choose_language(self, kod, popup):
        db.set_setting("jezik", kod)
        popup.dismiss()

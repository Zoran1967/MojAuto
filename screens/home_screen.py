from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import StringProperty

from database import db
from widgets import PrimaryButton, SecondaryButton
from translations import prevedi


class HomeScreen(Screen):
    """
    Početni ekran: dugmad za Novu listu, Istoriju, Bazu proizvoda/prodavnica
    i Podešavanja, plus dugme za izbor jezika.

    Napomena: go_to_new_list() vise NE brise automatski aktivnu listu ako
    je vec u toku (ima lista_id na shopping_list ekranu) - samo je
    nastavlja. Lista se brise/resetuje jedino kad korisnik eksplicitno
    zatvori listu (close_list na shopping_list ekranu).
    """

    JEZICI = [
        ("sr", "Srpski"),
        ("en", "English"),
        ("sk", "Slovencina"),
        ("uk", "Українська"),
    ]

    txt_new_list = StringProperty("")
    txt_history = StringProperty("")
    txt_database = StringProperty("")
    txt_settings = StringProperty("")
    txt_language_label = StringProperty("")

    def on_pre_enter(self, *args):
        self.osvezi_tekstove()

    def osvezi_tekstove(self):
        jezik = db.get_setting("jezik", "sr")
        self.txt_new_list = prevedi("home_new_list", jezik)
        self.txt_history = prevedi("home_history", jezik)
        self.txt_database = prevedi("home_database", jezik)
        self.txt_settings = prevedi("home_settings", jezik)
        self.txt_language_label = prevedi("home_language_label", jezik)

    def go_to_new_list(self):
        sl_screen = self.manager.get_screen("shopping_list")
        if sl_screen.lista_id is None:
            sl_screen.reset_for_new_list()
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

        trenutni = db.get_setting("jezik", "sr")

        for kod, naziv in self.JEZICI:
            is_current = kod == trenutni
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv}  (aktivan)" if is_current else naziv),
                size_hint_y=None, height=dp(48),
            )
            btn.bind(on_release=lambda inst, k=kod: self.choose_language(k))
            content.add_widget(btn)

        popup = Popup(
            title="Izaberi jezik / Select language",
            content=content, size_hint=(0.8, 0.6),
            overlay_color=(0, 0, 0, 0.85),
        )
        self._language_popup = popup
        popup.open()

    def choose_language(self, kod):
        db.set_setting("jezik", kod)
        self.osvezi_tekstove()
        if hasattr(self, "_language_popup"):
            self._language_popup.dismiss()

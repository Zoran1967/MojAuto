from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from database import db
from widgets import PrimaryButton, SecondaryButton


class HomeScreen(Screen):
    """
    Početni ekran: dugmad za Novu listu, Istoriju, Bazu proizvoda/prodavnica
    i Podešavanja, plus dugme za izbor jezika.
    """

    JEZICI = [
        ("sr", "Srpski"),
        ("en", "English"),
        ("sk", "Slovenčina"),
        ("uk", "Українська"),
    ]

    def go_to_new_list(self):
        self.manager.get_screen("shopping_list").reset_for_new_list()
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
        if hasattr(self, "_language_popup"):
            self._language_popup.dismiss()

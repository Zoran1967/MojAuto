from kivy.uix.screenmanager import Screen
from kivy.app import App

from theme import THEMES, PALETA
from database import db


class SettingsScreen(Screen):
    """Podesavanja - tema boje, pozadina ekrana, boja teksta u poljima, valuta i kurs."""

    def on_pre_enter(self, *args):
        self.build_theme_buttons()
        self.build_bg_buttons()
        self.build_input_text_buttons()
        self.build_currency_buttons()
        self.load_kurs()

    def build_theme_buttons(self):
        box = self.ids.theme_box
        box.clear_widgets()
        from widgets import PrimaryButton, SecondaryButton
        from kivy.metrics import dp

        app = App.get_running_app()
        for naziv in THEMES:
            is_current = naziv == app.theme.name
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv}  (aktivna)" if is_current else naziv),
                size_hint_y=None, height=dp(48),
            )
            btn.bind(on_release=lambda inst, n=naziv: self.choose_theme(n))
            box.add_widget(btn)

    def choose_theme(self, naziv):
        app = App.get_running_app()
        app.theme.set_theme(naziv)
        db.set_setting("tema", naziv)
        self.build_theme_buttons()

    # ---------- Boja pozadine ekrana ----------

    def build_bg_buttons(self):
        box = self.ids.bg_box
        box.clear_widgets()
        from widgets import PrimaryButton, SecondaryButton
        from kivy.metrics import dp

        app = App.get_running_app()
        for naziv in PALETA:
            is_current = naziv == app.theme.bg_name
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv}  (aktivna)" if is_current else naziv),
                size_hint_y=None, height=dp(44),
            )
            btn.bind(on_release=lambda inst, n=naziv: self.choose_bg_color(n))
            box.add_widget(btn)

    def choose_bg_color(self, naziv):
        app = App.get_running_app()
        uspeh = app.theme.set_bg_color(naziv)
        if not uspeh:
            self.ids.bg_error.text = "Ta boja je ista/slicna boji teksta u poljima - izaberi drugu."
            return
        self.ids.bg_error.text = ""
        db.set_setting("bg_boja", naziv)
        self.build_bg_buttons()

    # ---------- Boja teksta u poljima za unos ----------

    def build_input_text_buttons(self):
        box = self.ids.input_text_box
        box.clear_widgets()
        from widgets import PrimaryButton, SecondaryButton
        from kivy.metrics import dp

        app = App.get_running_app()
        for naziv in PALETA:
            is_current = naziv == app.theme.input_text_name
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv}  (aktivna)" if is_current else naziv),
                size_hint_y=None, height=dp(44),
            )
            btn.bind(on_release=lambda inst, n=naziv: self.choose_input_text_color(n))
            box.add_widget(btn)

    def choose_input_text_color(self, naziv):
        app = App.get_running_app()
        uspeh = app.theme.set_input_text_color(naziv)
        if not uspeh:
            self.ids.input_text_error.text = "Ta boja je ista/slicna boji pozadine - izaberi drugu."
            return
        self.ids.input_text_error.text = ""
        db.set_setting("input_boja", naziv)
        self.build_input_text_buttons()

    # ---------- Valuta ----------

    def build_currency_buttons(self):
        box = self.ids.currency_box
        box.clear_widgets()
        from widgets import PrimaryButton, SecondaryButton
        from kivy.metrics import dp

        trenutna = db.get_setting("valuta", "RSD")
        for naziv in ("RSD", "EUR"):
            is_current = naziv == trenutna
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv}  (aktivna)" if is_current else naziv),
                size_hint_y=None, height=dp(48),
            )
            btn.bind(on_release=lambda inst, n=naziv: self.choose_currency(n))
            box.add_widget(btn)

    def choose_currency(self, naziv):
        db.set_setting("valuta", naziv)
        self.build_currency_buttons()

    def load_kurs(self):
        kurs = db.get_setting("kurs", "117.5")
        self.ids.kurs_input.text = str(kurs)

    def save_kurs(self, tekst):
        tekst = tekst.strip().replace(",", ".")
        try:
            vrednost = float(tekst)
        except ValueError:
            return
        db.set_setting("kurs", str(vrednost))

    def go_back(self):
        self.manager.current = "home"

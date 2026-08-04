from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.metrics import dp

from theme import THEMES, PALETA
from database import db
from widgets import PrimaryButton, SecondaryButton, StyledTextInput


class SettingsScreen(Screen):
    """Podesavanja - glavni ekran ima 4 dugmeta, svako otvara podmeni popup."""

    def on_pre_enter(self, *args):
        self.ids.title_label.text = "Podesavanja"

    # ---------- Tema (boja dugmadi) ----------

    def open_theme_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        popup = Popup(
            title="Tema", content=content, size_hint=(0.85, 0.7),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            box.clear_widgets()
            app = App.get_running_app()
            for naziv in THEMES:
                is_current = naziv == app.theme.name
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " (aktivno)" if is_current else naziv),
                    size_hint_y=None, height=dp(48),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_theme(n, refresh))
                box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    def _choose_theme(self, naziv, refresh):
        app = App.get_running_app()
        app.theme.set_theme(naziv)
        db.set_setting("tema", naziv)
        refresh()

    # ---------- Boja pozadine ekrana ----------

    def open_bg_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title="Boja pozadine", content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            box.clear_widgets()
            app = App.get_running_app()
            for naziv in PALETA:
                is_current = naziv == app.theme.bg_name
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " (aktivno)" if is_current else naziv),
                    size_hint_y=None, height=dp(44),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_bg_color(n, error_label, refresh))
                box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    def _choose_bg_color(self, naziv, error_label, refresh):
        app = App.get_running_app()
        uspeh = app.theme.set_bg_color(naziv)
        if not uspeh:
            error_label.text = "Ta boja je vec zauzeta drugde."
            return
        error_label.text = ""
        db.set_setting("bg_boja", naziv)
        refresh()

    # ---------- Boja teksta u poljima za unos ----------

    def open_input_text_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title="Boja teksta u poljima", content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            box.clear_widgets()
            app = App.get_running_app()
            for naziv in PALETA:
                is_current = naziv == app.theme.input_text_name
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " (aktivno)" if is_current else naziv),
                    size_hint_y=None, height=dp(44),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_input_text_color(n, error_label, refresh))
                box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    def _choose_input_text_color(self, naziv, error_label, refresh):
        app = App.get_running_app()
        uspeh = app.theme.set_input_text_color(naziv)
        if not uspeh:
            error_label.text = "Ta boja je vec zauzeta drugde."
            return
        error_label.text = ""
        db.set_setting("input_boja", naziv)
        refresh()

    # ---------- Valuta ----------

    def open_currency_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        currency_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        content.add_widget(currency_box)

        kurs_label = Label(
            text="Kurs (1 EUR = ? RSD)", font_size="14sp",
            size_hint_y=None, height=dp(28), color=(0.7, 0.7, 0.7, 1),
        )
        content.add_widget(kurs_label)

        kurs_input = StyledTextInput(
            text=str(db.get_setting("kurs", "117.5")),
            multiline=False, input_filter="float",
            size_hint_y=None, height=dp(48),
        )
        content.add_widget(kurs_input)

        def save_kurs(*a):
            tekst = kurs_input.text.strip().replace(",", ".")
            try:
                vrednost = float(tekst)
            except ValueError:
                return
            db.set_setting("kurs", str(vrednost))

        kurs_input.bind(on_text_validate=save_kurs)
        kurs_input.bind(focus=lambda inst, val: None if val else save_kurs())

        popup = Popup(
            title="Valuta", content=content, size_hint=(0.85, 0.55),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def refresh_currency():
            currency_box.clear_widgets()
            trenutna = db.get_setting("valuta", "RSD")
            for naziv in ("RSD", "EUR"):
                is_current = naziv == trenutna
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " (aktivno)" if is_current else naziv),
                    size_hint_y=None, height=dp(48),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_currency(n, refresh_currency))
                currency_box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=lambda inst: (save_kurs(), popup.dismiss()))
        content.add_widget(close_btn)

        refresh_currency()
        popup.open()

    def _choose_currency(self, naziv, refresh):
        db.set_setting("valuta", naziv)
        refresh()

    def go_back(self):
        self.manager.current = "home"

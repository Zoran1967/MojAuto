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
from translations import prevedi


def _jezik():
    return db.get_setting("jezik", "sr")


class SettingsScreen(Screen):
    """Podesavanja - glavni ekran ima 4 dugmeta, svako otvara podmeni popup.
    Tekstovi se prevode preko translations.prevedi() prema trenutno
    izabranom jeziku."""

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.title_label.text = prevedi("podesavanja_naslov", jezik)
        self.ids.tema_btn.text = prevedi("podesavanja_tema_btn", jezik)
        self.ids.bg_btn.text = prevedi("podesavanja_pozadina_btn", jezik)
        self.ids.tekst_btn.text = prevedi("podesavanja_tekst_btn", jezik)
        self.ids.kurs_btn.text = prevedi("podesavanja_kurs_btn", jezik)
        self.ids.backup_btn.text = prevedi("podesavanja_backup_btn", jezik)
        self.ids.restore_btn.text = prevedi("podesavanja_restore_btn", jezik)
        self.ids.back_btn.text = prevedi("istorija_nazad", jezik)

    # ---------- Tema (boja dugmadi) ----------

    def open_theme_popup(self):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        popup = Popup(
            title=prevedi("podesavanja_tema_naslov", jezik), content=content, size_hint=(0.85, 0.7),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            box.clear_widgets()
            app = App.get_running_app()
            for naziv in THEMES:
                is_current = naziv == app.theme.name
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " " + prevedi("podesavanja_aktivno", jezik) if is_current else naziv),
                    size_hint_y=None, height=dp(48),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_theme(n, refresh))
                box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("podesavanja_zatvori", jezik), size_hint_y=None, height=dp(44))
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
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("podesavanja_pozadina_naslov", jezik), content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            box.clear_widgets()
            app = App.get_running_app()
            for naziv in PALETA:
                is_current = naziv == app.theme.bg_name
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " " + prevedi("podesavanja_aktivno", jezik) if is_current else naziv),
                    size_hint_y=None, height=dp(44),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_bg_color(n, error_label, refresh))
                box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("podesavanja_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    def _choose_bg_color(self, naziv, error_label, refresh):
        jezik = _jezik()
        app = App.get_running_app()
        uspeh = app.theme.set_bg_color(naziv)
        if not uspeh:
            error_label.text = prevedi("podesavanja_boja_zauzeta", jezik)
            return
        error_label.text = ""
        db.set_setting("bg_boja", naziv)
        refresh()

    # ---------- Boja teksta u poljima za unos ----------

    def open_input_text_popup(self):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(box)
        content.add_widget(scroll)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("podesavanja_tekst_naslov", jezik), content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            box.clear_widgets()
            app = App.get_running_app()
            for naziv in PALETA:
                is_current = naziv == app.theme.input_text_name
                btn_cls = PrimaryButton if is_current else SecondaryButton
                btn = btn_cls(
                    text=(naziv + " " + prevedi("podesavanja_aktivno", jezik) if is_current else naziv),
                    size_hint_y=None, height=dp(44),
                )
                btn.bind(on_release=lambda inst, n=naziv: self._choose_input_text_color(n, error_label, refresh))
                box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("podesavanja_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    def _choose_input_text_color(self, naziv, error_label, refresh):
        jezik = _jezik()
        app = App.get_running_app()
        uspeh = app.theme.set_input_text_color(naziv)
        if not uspeh:
            error_label.text = prevedi("podesavanja_boja_zauzeta", jezik)
            return
        error_label.text = ""
        db.set_setting("input_boja", naziv)
        refresh()

    # ---------- Kurs (koristi se samo kad korisnik rucno trazi prikaz u drugoj valuti) ----------

    def open_currency_popup(self):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        info_label = Label(
            text=prevedi("podesavanja_kurs_info", jezik),
            font_size="13sp", color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
        )
        info_label.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(10)),
        )
        content.add_widget(info_label)

        kurs_label = Label(
            text=prevedi("podesavanja_kurs_label", jezik), font_size="14sp",
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
            title=prevedi("podesavanja_kurs_naslov", jezik), content=content, size_hint=(0.85, 0.5),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        close_btn = SecondaryButton(text=prevedi("podesavanja_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=lambda inst: (save_kurs(), popup.dismiss()))
        content.add_widget(close_btn)

        popup.open()

    # ---------- Rezervna kopija (backup / restore) ----------

    def _prikazi_poruku(self, tekst):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        label = Label(text=tekst, font_size="14sp", size_hint_y=None)
        label.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(10)),
        )
        content.add_widget(label)

        popup = Popup(
            title="", content=content, size_hint=(0.85, 0.4),
            overlay_color=(0, 0, 0, 0.85),
        )
        close_btn = SecondaryButton(text=prevedi("podesavanja_zatvori", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def napravi_backup(self):
        jezik = _jezik()
        try:
            putanja = db.napravi_rezervnu_kopiju()
            self._prikazi_poruku(prevedi("podesavanja_backup_sacuvan", jezik).format(putanja=putanja))
        except Exception as e:
            self._prikazi_poruku(prevedi("podesavanja_backup_greska", jezik).format(greska=str(e)))

    def vrati_backup(self):
        jezik = _jezik()
        try:
            uspeh = db.vrati_rezervnu_kopiju()
            if uspeh:
                self._prikazi_poruku(prevedi("podesavanja_backup_vracen", jezik))
            else:
                self._prikazi_poruku(prevedi("podesavanja_backup_nema", jezik))
        except Exception as e:
            self._prikazi_poruku(prevedi("podesavanja_backup_greska", jezik).format(greska=str(e)))

    def go_back(self):
        self.manager.current = "home"

"""
Shopping App - glavni fajl
Faza 3: profi izgled (tema boja, zaobljeni dugmici), istorija po
prodavnicama sa stavkama, podesavanja.
"""
import os
import traceback

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import ObjectProperty

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle


def _napravi_greska_sadrzaj(greska_tekst):
    """Pravi BoxLayout sa belom pozadinom i crnim tekstom - uvek citljivo
    bez obzira na trenutnu temu boja aplikacije. Sirina teksta prati
    sirinu ekrana (Window.width) umesto fiksnog broja piksela, da se
    tekst ne bi zbio u usku, neciljivu kolonu na velikim ekranima."""
    content = BoxLayout(orientation="vertical", padding=10, spacing=10)

    with content.canvas.before:
        Color(1, 1, 1, 1)
        bg_rect = Rectangle(pos=content.pos, size=content.size)
    content.bind(pos=lambda inst, val: setattr(bg_rect, "pos", val))
    content.bind(size=lambda inst, val: setattr(bg_rect, "size", val))

    scroll = ScrollView()
    label = Label(
        text=greska_tekst,
        size_hint_y=None,
        size_hint_x=1,
        halign="left",
        valign="top",
        color=(0, 0, 0, 1),
        font_size="13sp",
    )

    def _osvezi_sirinu(*a):
        label.text_size = (Window.width - 40, None)

    def _osvezi_visinu(*a):
        label.height = label.texture_size[1]

    label.bind(texture_size=_osvezi_visinu)
    Window.bind(width=_osvezi_sirinu)
    _osvezi_sirinu()

    scroll.add_widget(label)
    content.add_widget(scroll)
    return content


class CrashPopupHandler(ExceptionHandler):
    """Hvata greske koje se dese DOK app vec radi (npr. klik na dugme)."""

    def handle_exception(self, inst):
        greska = traceback.format_exc()
        print(greska)

        content = _napravi_greska_sadrzaj(greska)
        popup = Popup(title="Greska (kopiraj i posalji)", content=content, size_hint=(0.95, 0.95))
        popup.open()

        return ExceptionManager.PASS


ExceptionManager.add_handler(CrashPopupHandler())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class CrashApp(App):
    """Minimalna app koja samo prikazuje tekst greske - koristi se ako
    glavna aplikacija ne uspe da se pokrene (npr. greska u kv fajlu,
    u theme.py, ili slicno) - da se app ne bi samo ugasila bez poruke."""

    def __init__(self, greska_tekst, **kwargs):
        super().__init__(**kwargs)
        self.greska_tekst = greska_tekst

    def build(self):
        return _napravi_greska_sadrzaj(self.greska_tekst)


def pokreni_glavnu_app():
    from screens.home_screen import HomeScreen
    from screens.shopping_list_screen import ShoppingListScreen
    from screens.history_screen import HistoryScreen
    from screens.database_screen import DatabaseScreen
    from screens.settings_screen import SettingsScreen
    from database import db
    from theme import Theme
    import widgets  # noqa: F401

    db.init_db()

    Builder.load_file(os.path.join(BASE_DIR, "kv", "home_screen.kv"))
    Builder.load_file(os.path.join(BASE_DIR, "kv", "shopping_list_screen.kv"))
    Builder.load_file(os.path.join(BASE_DIR, "kv", "history_screen.kv"))
    Builder.load_file(os.path.join(BASE_DIR, "kv", "database_screen.kv"))
    Builder.load_file(os.path.join(BASE_DIR, "kv", "settings_screen.kv"))

    Builder.load_string("""
<StyledTextInput>:
    foreground_color: app.theme.input_text_color
""")

    class ShoppingApp(App):
        theme = ObjectProperty(None)
        assets_dir = ObjectProperty(None)

        def build(self):
            if platform not in ("android", "ios"):
                Window.size = (400, 700)

            self.assets_dir = os.path.join(BASE_DIR, "assets") + os.sep

            self.theme = Theme()

            sacuvana_tema = db.get_setting("tema", self.theme.name)
            self.theme.set_theme(sacuvana_tema)

            sacuvana_bg = db.get_setting("bg_boja", self.theme.bg_name)
            self.theme.set_bg_color(sacuvana_bg)

            sacuvan_input_tekst = db.get_setting("input_boja", self.theme.input_text_name)
            self.theme.set_input_text_color(sacuvan_input_tekst)

            Window.clearcolor = tuple(self.theme.bg_color)
            self.theme.bind(bg_color=self._on_bg_color_change)

            sm = ScreenManager(transition=FadeTransition())
            sm.add_widget(HomeScreen(name="home"))
            sm.add_widget(ShoppingListScreen(name="shopping_list"))
            sm.add_widget(HistoryScreen(name="history"))
            sm.add_widget(DatabaseScreen(name="database"))
            sm.add_widget(SettingsScreen(name="settings"))
            sm.current = "home"
            return sm

        def _on_bg_color_change(self, instance, value):
            Window.clearcolor = tuple(value)

    ShoppingApp().run()


if __name__ == "__main__":
    try:
        pokreni_glavnu_app()
    except Exception:
        greska = traceback.format_exc()
        print(greska)
        CrashApp(greska).run()

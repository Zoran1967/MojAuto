"""
Shopping App - glavni fajl
Faza 3: profi izgled (tema boja, zaobljeni dugmici), istorija po
prodavnicama sa stavkama, podesavanja.
"""
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import ObjectProperty

from screens.home_screen import HomeScreen
from screens.shopping_list_screen import ShoppingListScreen
from screens.history_screen import HistoryScreen
from screens.database_screen import DatabaseScreen
from screens.settings_screen import SettingsScreen
from database import db
from theme import Theme
import widgets  # noqa: F401 - registruje PrimaryButton/SecondaryButton/DangerButton/Card u kv

import traceback
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


class CrashPopupHandler(ExceptionHandler):
    def handle_exception(self, inst):
        greska = traceback.format_exc()
        print(greska)

        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        scroll = ScrollView()
        label = Label(
            text=greska,
            size_hint_y=None,
            text_size=(400, None),
            halign="left",
            valign="top",
        )
        label.bind(texture_size=lambda inst, val: setattr(label, "height", val[1]))
        scroll.add_widget(label)
        content.add_widget(scroll)

        popup = Popup(title="Greska (kopiraj i posalji)", content=content, size_hint=(0.95, 0.95))
        popup.open()

        return ExceptionManager.PASS


ExceptionManager.add_handler(CrashPopupHandler())
db.init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

Builder.load_file(os.path.join(BASE_DIR, "kv", "home_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "shopping_list_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "history_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "database_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "settings_screen.kv"))

# Boja teksta u svim StyledTextInput poljima prati izabranu temu
# (app.theme.input_text_color) - automatski se osvezava kad se promeni.
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


if __name__ == "__main__":
    ShoppingApp().run()

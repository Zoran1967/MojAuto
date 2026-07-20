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

db.init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

Builder.load_file(os.path.join(BASE_DIR, "kv", "home_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "shopping_list_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "history_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "database_screen.kv"))
Builder.load_file(os.path.join(BASE_DIR, "kv", "settings_screen.kv"))


class ShoppingApp(App):
    theme = ObjectProperty(None)
    assets_dir = ObjectProperty(None)

    def build(self):
        if platform not in ("android", "ios"):
            Window.size = (400, 700)
        # Malo profesionalnija pozadina umesto cistog

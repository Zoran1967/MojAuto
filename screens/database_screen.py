from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.app import App

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput


class IconTabButton(ButtonBehavior, BoxLayout):
    """Dugme sa ikonicom iznad teksta, koristi se za dodatne tabove
    (Gume, Registracija, Osiguranje, Akumulator, Kvarovi, Dokumenta)."""

    def __init__(self, icon_source, text, **kwargs):
        super().__init__(orientation="vertical", padding=dp(4), spacing=dp(2), **kwargs)
        self.icon_source = icon_source
        self.label_text = text
        self.add_widget(KivyImage(source=icon_source, allow_stretch=True, keep_ratio=True, size_hint_y=0.7))
        self.add_widget(Label(
            text=text, font_size="11sp", bold=True, size_hint_y=0.3,
            halign="center", valign="middle", text_size=(dp(84), None),
        ))


class DatabaseScreen(Screen):
    """
    Ekran za unos zapisa po vozilu, sa tabovima: Gorivo, Servisi,
    Troskovi (glavna 3 dugmeta iz kv fajla) i Gume, Registracija,
    Osiguranje, Akumulator, Kvarovi, Dokumenta (dinamicki dodati
    u extra_tabs_box, sa ikonicama).
    """

    TAB_DEFS = {
        "gorivo": {
            "naslov": "Gorivo",
            "fields": [
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("kilometraza", "Kilometraza",

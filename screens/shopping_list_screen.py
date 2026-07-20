            from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from widgets import PrimaryButton, SecondaryButton, StyledTextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db


class ShoppingListScreen(Screen):
    """
    Ekran aktivne liste za kupovinu.
    Izbor prodavnice, dodavanje proizvoda (autopopuna zadnje cene iz baze),
    racunanje totala, cuvanje zatvorene liste u istoriju.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lista_id = None
        self.prodavnica_id = None
        self.stavke_total = 0.0

    def on_pre_enter(self, *args):
        if self.lista_id is None:
            self.open_store_picker()

    def reset_for_new_list(self):
        self.lista_id = None
        self.prodavnica_id = None
        self.stavke_total = 0.0
        self.ids.items_box.clear_widgets()
        self.ids.store_label.text = "Prodavnica: (izbor dolazi)"
        self.ids.total_label.text = "0.00"

    # ------

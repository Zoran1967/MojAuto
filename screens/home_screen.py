from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


class HomeScreen(Screen):
    """
    Pocetni ekran: dugmad za Vozila, Istoriju, Zapise (gorivo/servisi/troskovi)
    i Podesavanja.
    """

    txt_new_list = StringProperty("Vozila")
    txt_history = StringProperty("Istorija")
    txt_database = StringProperty("Zapisi")
    txt_settings = StringProperty("Podesavanja")

    def on_pre_enter(self, *args):
        pass

    def go_to_new_list(self):
        self.manager.current = "shopping_list"

    def go_to_history(self):
        self.manager.current = "history"

    def go_to_database(self):
        self.manager.current = "database"

    def go_to_settings(self):
        self.manager.current = "settings"

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db
from widgets import SecondaryButton, DangerButton


class HistoryScreen(Screen):
    """
    Istorija servisa i troskova - organizovano po vozilu.
    Prikazuje vozila; klik na vozilo otvara sve servise i troskove
    tog vozila, sortirano po datumu (najnoviji prvi).
    """

    def on_pre_enter(self, *args):
        self.ids.title_label.text = "Istorija servisa i troskova"
        self.load_history()

    def load_history(self):
        box = self.ids.history_box
        box.clear_widgets()
        vozila = db.get_all("vozila", order_by="marka")

        if not vozila:
            box.add_widget(
                Label(
                    text="Nema dodatih vozila.",
                    size_hint_y=None, height=dp(60), color=(0.7, 0.7, 0.7, 1),
                )
            )
            return

        for vozilo in vozila:
            broj_zapisa = len(db.get_by_vehicle("servisi", vozilo["id"])) + len(
                db.get_by_vehicle("troskovi", vozilo["id"])
            )
            btn = SecondaryButton(
                text=f"{vozilo['marka']} {vozilo['model']} ({broj_zapisa} zapisa)",
                size_hint_y=None, height=dp(52), font_size="16sp",
            )
            btn.bind(
                on_release=lambda inst, vid=vozilo["id"], naziv=f"{vozilo['marka']} {vozilo['model']}":
                    self.open_vehicle_history(vid, naziv)
            )
            box.add_widget(btn)

    # ---------- Nivo 1: zapisi jednog vozila ----------

    def open_vehicle_history(self, vehicle_id, naziv_vozila):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(
            Label(text=naziv_vozila, bold=True, font_size="18sp",
                  size_hint_y=None, height=dp(32))
        )

        records_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        records_box.bind(minimum_height=records_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(records_box)
        content.add_widget(scroll)

        popup = Popup(
            title="Zapisi vozila", content=content, size_hint=(0.92, 0.8),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh_records():
            records_box.clear_widgets()

            servisi = [("servisi", r) for r in db.get_by_vehicle("servisi", vehicle_id)]
            troskovi = [("troskovi", r) for r in db.get_by_vehicle("troskovi", vehicle_id)]
            svi = servisi + troskovi
            svi.sort(key=lambda x: x[1]["datum"], reverse=True)

            if not svi:
                popup.dismiss()
                self.load_history()
                return

            for tabela, red in svi:
                if tabela == "servisi":
                    tekst = f"{red['datum']} - {red['tip']}: {red['ukupna_cena']} din"
                else:
                    tekst = f"{red['datum']} - {red['vrsta']}: {red['iznos']} din"

                btn = SecondaryButton(
                    text=tekst, size_hint_y=None, height=dp(56), halign="center",
                )
                btn.bind(
                    on_release=lambda inst, t=tabela, rid=red["id"]:
                        self.open_record_detail(t, rid, popup, refresh_records)
                )
                records_box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh_records()
        popup.open()

    # ---------- Nivo 2: detalji jednog zapisa ----------

    def open_record_detail(self, tabela, record_id, parent_popup, refresh_parent):
        red = db.get_by_id(tabela, record_id)
        if red is None:
            return

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        if tabela == "servisi":
            content.add_widget(Label(text=f"{red['datum']} - {red['tip']}", bold=True, font_size="16sp", size_hint_y=None, height=dp(28)))
            content.add_widget(Label(text=f"Naziv: {red['naziv'] or '-'}", size_hint_y=None, height=dp(28)))
            content.add_widget(Label(text=f"Opis: {red['opis'] or '-'}", size_hint_y=None, height=dp(28)))
            content.add_widget(Label(text=f"Ukupna cena: {red['ukupna_cena']} din", bold=True, size_hint_y=None, height=dp(28)))
        else:
            content.add_widget(Label(text=f"{red['datum']} - {red['vrsta']}", bold=True, font_size="16sp", size_hint_y=None, height=dp(28)))
            content.add_widget(Label(text=f"Napomena: {red['napomena'] or '-'}", size_hint_y=None, height=dp(28)))
            content.add_widget(Label(text=f"Iznos: {red['iznos']} din", bold=True, size_hint_y=None, height=dp(28)))

        detail_popup = Popup(
            title="Detalji zapisa", content=content, size_hint=(0.9, 0.6),
            overlay_color=(0, 0, 0, 0.85),
        )

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = "Potvrdi brisanje"
                return
            db.delete(tabela, record_id)
            detail_popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        back_btn = SecondaryButton(text="Nazad")
        back_btn.bind(on_release=detail_popup.dismiss)
        delete_btn = DangerButton(text="Obrisi zapis")
        delete_btn.bind(on_release=delete)
        btn_row.add_widget(back_btn)
        btn_row.add_widget(delete_btn)
        content.add_widget(btn_row)

        detail_popup.open()

    def go_back(self):
        self.manager.current = "home"

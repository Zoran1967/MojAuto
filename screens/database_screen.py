from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput


class DatabaseScreen(Screen):
    """
    Ekran za unos zapisa po vozilu, sa tri taba: Gorivo, Servisi, Troskovi.
    Svaki tab prikazuje vozila; klik na vozilo otvara zapise tog tipa
    za to vozilo, sa dodavanjem/izmenom/brisanjem.
    """

    TAB_DEFS = {
        "gorivo": {
            "naslov": "Gorivo",
            "fields": [
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("kilometraza", "Kilometraza", "int"),
                ("litara", "Litara", "float"),
                ("cena_po_litru", "Cena po litru", "float"),
                ("pumpa", "Pumpa", "text"),
                ("grad", "Grad", "text"),
            ],
            "prikaz": lambda r: f"{r['datum']} - {r['litara']} L - {r['ukupna_cena']} din",
        },
        "servisi": {
            "naslov": "Servisi",
            "fields": [
                ("tip", "Tip servisa", "text"),
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("kilometraza", "Kilometraza", "int"),
                ("naziv", "Naziv", "text"),
                ("opis", "Opis", "text"),
                ("cena_delova", "Cena delova", "float"),
                ("cena_rada", "Cena rada", "float"),
            ],
            "prikaz": lambda r: f"{r['datum']} - {r['tip']} - {r['ukupna_cena']} din",
        },
        "troskovi": {
            "naslov": "Troskovi",
            "fields": [
                ("vrsta", "Vrsta troska", "text"),
                ("iznos", "Iznos", "float"),
                ("datum", "Datum (DD.MM.GGGG)", "text"),
                ("napomena", "Napomena", "text"),
            ],
            "prikaz": lambda r: f"{r['datum']} - {r['vrsta']} - {r['iznos']} din",
        },
    }

    def on_pre_enter(self, *args):
        self.ids.title_label.text = "Zapisi vozila"
        self.ids.tab_products.text = "Gorivo"
        self.ids.tab_stores.text = "Servisi"
        self.ids.tab_categories.text = "Troskovi"
        self.show_proizvodi()

    # ---------- Tabovi (nazivi metoda zadrzani zbog kv fajla) ----------

    def show_proizvodi(self):
        self._prikazi_vozila_za_tab("gorivo")

    def show_prodavnice(self):
        self._prikazi_vozila_za_tab("servisi")

    def show_kategorije(self):
        self._prikazi_vozila_za_tab("troskovi")

    def _prikazi_vozila_za_tab(self, tabela):
        box = self.ids.database_box
        box.clear_widgets()

        vozila = db.get_all("vozila", order_by="marka")
        if not vozila:
            box.add_widget(Label(
                text="Nema dodatih vozila.", size_hint_y=None,
                height=dp(40), color=(1, 1, 1, 1),
            ))
            return

        for vozilo in vozila:
            btn = Button(
                text=f"{vozilo['marka']} {vozilo['model']}",
                size_hint_y=None, height=dp(46),
                background_normal="", background_color=(0.18, 0.18, 0.22, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(
                on_release=lambda inst, vid=vozilo["id"], vnaziv=f"{vozilo['marka']} {vozilo['model']}":
                    self.open_records_popup(tabela, vid, vnaziv)
            )
            box.add_widget(btn)

    # ---------- Zapisi jednog vozila (za dati tab) ----------

    def open_records_popup(self, tabela, vehicle_id, vozilo_naziv):
        tab_def = self.TAB_DEFS[tabela]
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        content.add_widget(Label(
            text=f"{vozilo_naziv} - {tab_def['naslov']}", bold=True, font_size="18sp",
            size_hint_y=None, height=dp(32),
        ))

        records_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        records_box.bind(minimum_height=records_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(records_box)
        content.add_widget(scroll)

        popup = Popup(
            title=tab_def["naslov"], content=content, size_hint=(0.94, 0.85),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh():
            records_box.clear_widgets()
            zapisi = db.get_by_vehicle(tabela, vehicle_id, order_by="id DESC")
            if not zapisi:
                records_box.add_widget(Label(
                    text="Nema zapisa.", size_hint_y=None,
                    height=dp(36), color=(0.75, 0.75, 0.75, 1),
                ))
            for red in zapisi:
                btn = SecondaryButton(
                    text=tab_def["prikaz"](red), size_hint_y=None, height=dp(52),
                )
                btn.bind(
                    on_release=lambda inst, rid=red["id"]:
                        self.open_edit_record_popup(tabela, rid, vehicle_id, popup, refresh)
                )
                records_box.add_widget(btn)

        novi_btn = PrimaryButton(text="+ Dodaj zapis", size_hint_y=None, height=dp(44))
        novi_btn.bind(
            on_release=lambda inst: self.open_add_record_popup(tabela, vehicle_id, popup, refresh)
        )
        content.add_widget(novi_btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh()
        popup.open()

    # ---------- Dodavanje / izmena zapisa ----------

    def _build_form(self, tabela, existing=None):
        tab_def = self.TAB_DEFS[tabela]
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        inputs = {}
        for key, label, tip in tab_def["fields"]:
            vrednost = ""
            if existing is not None and existing[key] is not None:
                vrednost = str(existing[key])
            tf = StyledTextInput(
                text=vrednost, hint_text=label,
                input_filter=("float" if tip == "float" else "int" if tip == "int" else None),
                multiline=False, size_hint_y=None, height=dp(44),
            )
            inputs[key] = tf
            content.add_widget(tf)

        return content, inputs

    def _collect_data(self, tabela, inputs):
        tab_def = self.TAB_DEFS[tabela]
        data = {}
        for key, _label, tip in tab_def["fields"]:
            tekst = inputs[key].text.strip()
            if tip == "int":
                data[key] = int(tekst) if tekst else None
            elif tip == "float":
                data[key] = float(tekst.replace(",", ".")) if tekst else 0.0
            else:
                data[key] = tekst
        return data

    def open_add_record_popup(self, tabela, vehicle_id, parent_popup, refresh_parent):
        content, inputs = self._build_form(tabela)
        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        scroll_wrap = ScrollView(size_hint=(1, None), height=dp(400))
        scroll_wrap.add_widget(content)
        outer = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        outer.add_widget(scroll_wrap)

        popup = Popup(
            title="Novi zapis", content=outer, size_hint=(0.9, 0.85),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            data = self._collect_data(tabela, inputs)
            if tabela == "gorivo":
                data["ukupna_cena"] = round(data.get("litara", 0) * data.get("cena_po_litru", 0), 2)
                data["pun_rezervoar"] = 1
            elif tabela == "servisi":
                data["ukupna_cena"] = round(data.get("cena_delova", 0) + data.get("cena_rada", 0), 2)
            data["vehicle_id"] = vehicle_id
            db.insert(tabela, data)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        outer.add_widget(btn_row)

        popup.open()

    def open_edit_record_popup(self, tabela, record_id, vehicle_id, parent_popup, refresh_parent):
        red = db.get_by_id(tabela, record_id)
        if red is None:
            return

        content, inputs = self._build_form(tabela, existing=red)
        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        scroll_wrap = ScrollView(size_hint=(1, None), height=dp(400))
        scroll_wrap.add_widget(content)
        outer = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        outer.add_widget(scroll_wrap)

        popup = Popup(
            title="Izmeni zapis", content=outer, size_hint=(0.9, 0.85),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            data = self._collect_data(tabela, inputs)
            if tabela == "gorivo":
                data["ukupna_cena"] = round(data.get("litara", 0) * data.get("cena_po_litru", 0), 2)
            elif tabela == "servisi":
                data["ukupna_cena"] = round(data.get("cena_delova", 0) + data.get("cena_rada", 0), 2)
            db.update(tabela, record_id, data)
            popup.dismiss()
            refresh_parent()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = "Potvrdi brisanje"
                return
            db.delete(tabela, record_id)
            popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        outer.add_widget(btn_row)

        delete_btn = DangerButton(text="Obrisi zapis", size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        outer.add_widget(delete_btn)

        popup.open()

    def go_back(self):
        self.manager.current = "home"

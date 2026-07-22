from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, Card
from translations import prevedi


def _jezik():
    return db.get_setting("jezik", "sr")


class HistoryScreen(Screen):
    """
    Istorija kupovina - organizovano po prodavnicama.
    Napomena o valutama: sve vrednosti dolaze iz baze UVEK u RSD i
    prikazuju se konvertovane preko db.rsd_u_prikaz().
    Tekstovi se prevode preko prevedi() prema trenutno izabranom jeziku.
    """

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.title_label.text = prevedi("hist_title", jezik)
        self.load_history()

    def load_history(self):
        jezik = _jezik()
        box = self.ids.history_box
        box.clear_widgets()
        prodavnice = db.get_prodavnice_sa_istorijom()

        if not prodavnice:
            box.add_widget(
                Label(
                    text=prevedi("hist_empty", jezik),
                    size_hint_y=None, height=dp(60), color=(0.7, 0.7, 0.7, 1),
                )
            )
            return

        for pid, naziv, broj_racuna in prodavnice:
            btn = SecondaryButton(
                text=prevedi("hist_receipts_count", jezik).format(naziv=naziv, broj=broj_racuna),
                size_hint_y=None, height=dp(52), font_size="16sp",
            )
            btn.bind(
                on_release=lambda inst, pid=pid, naziv=naziv: self.open_store_history(pid, naziv)
            )
            box.add_widget(btn)

    # ---------- Nivo 1: racuni jedne prodavnice ----------

    def open_store_history(self, prodavnica_id, naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(
            Label(text=naziv, bold=True, font_size="18sp",
                  size_hint_y=None, height=dp(32))
        )

        receipts_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        receipts_box.bind(minimum_height=receipts_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(receipts_box)
        content.add_widget(scroll)

        popup = Popup(
            title=prevedi("hist_receipts_popup_title", jezik), content=content, size_hint=(0.92, 0.8),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh_receipts():
            receipts_box.clear_widgets()
            liste = db.get_liste_za_prodavnicu(prodavnica_id)
            if not liste:
                popup.dismiss()
                self.load_history()
                return
            for lista_id, datum, ukupno_rsd in liste:
                ukupno_prikaz = db.rsd_u_prikaz(ukupno_rsd)
                btn = SecondaryButton(
                    text=prevedi("hist_receipt_total", jezik).format(
                        datum=datum, ukupno=f"{ukupno_prikaz:.2f}", valuta=db.valuta_oznaka()
                    ),
                    size_hint_y=None, height=dp(56), halign="center",
                )
                btn.bind(
                    on_release=lambda inst, lid=lista_id, d=datum, u=ukupno_rsd:
                        self.open_receipt_detail(lid, d, u, popup, refresh_receipts)
                )
                receipts_box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("hist_close", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh_receipts()
        popup.open()

    # ---------- Nivo 2: stavke jednog racuna ----------

    def open_receipt_detail(self, lista_id, datum, ukupno_rsd, parent_popup, refresh_parent):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(
            Label(text=datum, bold=True, font_size="16sp",
                  size_hint_y=None, height=dp(28))
        )

        header = BoxLayout(size_hint_y=None, height=dp(30))
        header.add_widget(Label(text=prevedi("hist_col_product", jezik), bold=True, font_size="13sp"))
        header.add_widget(Label(text=prevedi("hist_col_qty", jezik), bold=True, size_hint_x=0.4, font_size="13sp"))
        header.add_widget(Label(
            text=prevedi("hist_col_price", jezik).format(valuta=db.valuta_oznaka()),
            bold=True, size_hint_x=0.5, font_size="13sp"
        ))
        header.add_widget(Label(text=prevedi("hist_col_total", jezik), bold=True, size_hint_x=0.5, font_size="13sp"))
        content.add_widget(header)

        items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        items_box.bind(minimum_height=items_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(items_box)
        content.add_widget(scroll)

        stavke = db.get_lista_stavke(lista_id)
        for naziv, kolicina, cena_rsd, total_rsd in stavke:
            row = BoxLayout(size_hint_y=None, height=dp(36))
            row.add_widget(Label(text=naziv, font_size="13sp"))
            row.add_widget(Label(text=f"{kolicina:g}", size_hint_x=0.4, font_size="13sp"))
            row.add_widget(Label(text=f"{db.rsd_u_prikaz(cena_rsd):.2f}", size_hint_x=0.5, font_size="13sp"))
            row.add_widget(Label(text=f"{db.rsd_u_prikaz(total_rsd):.2f}", size_hint_x=0.5, font_size="13sp"))
            items_box.add_widget(row)

        total_row = BoxLayout(size_hint_y=None, height=dp(36))
        total_row.add_widget(Label(text=prevedi("hist_total_label", jezik), bold=True))
        total_row.add_widget(Label(text=f"{db.rsd_u_prikaz(ukupno_rsd):.2f} {db.valuta_oznaka()}", bold=True))
        content.add_widget(total_row)

        detail_popup = Popup(
            title=prevedi("hist_receipt_popup_title", jezik), content=content, size_hint=(0.94, 0.85),
            overlay_color=(0, 0, 0, 0.85),
        )

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("hist_confirm_delete", jezik)
                return
            db.delete_lista(lista_id)
            detail_popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        back_btn = SecondaryButton(text=prevedi("hist_back", jezik))
        back_btn.bind(on_release=detail_popup.dismiss)
        delete_btn = DangerButton(text=prevedi("hist_delete_receipt", jezik))
        delete_btn.bind(on_release=delete)
        btn_row.add_widget(back_btn)
        btn_row.add_widget(delete_btn)
        content.add_widget(btn_row)

        detail_popup.open()

    def go_back(self):
        self.manager.current = "home"

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db
from widgets import SecondaryButton, DangerButton


SVE_TABELE = [
    "gorivo", "servisi", "troskovi", "gume", "registracija",
    "osiguranje", "akumulator", "kvarovi", "dokumenti", "podsetnici",
]

DATUM_POLJE = {
    "gorivo": "datum",
    "servisi": "datum",
    "troskovi": "datum",
    "gume": "datum_kupovine",
    "registracija": "datum_registracije",
    "osiguranje": "datum",
    "akumulator": "datum_kupovine",
    "kvarovi": "datum",
    "dokumenti": "datum_dodavanja",
    "podsetnici": "datum_isteka",
}

NASLOVI = {
    "gorivo": "Gorivo",
    "servisi": "Servis",
    "troskovi": "Trosak",
    "gume": "Gume",
    "registracija": "Registracija",
    "osiguranje": "Osiguranje",
    "akumulator": "Akumulator",
    "kvarovi": "Kvar",
    "dokumenti": "Dokument",
    "podsetnici": "Podsetnik",
}


def _novcani_prikaz(vrednost):
    return f"{db.rsd_u_prikaz(vrednost):.2f} {db.valuta_oznaka()}"


def _kratak_opis(tabela, red):
    naslov = NASLOVI[tabela]
    datum = red[DATUM_POLJE[tabela]] or "-"

    if tabela == "gorivo":
        return f"{naslov}: {datum} - {red['litara']} L - {_novcani_prikaz(red['ukupna_cena'])}"
    if tabela == "servisi":
        return f"{naslov}: {datum} - {red['tip']} - {_novcani_prikaz(red['ukupna_cena'])}"
    if tabela == "troskovi":
        return f"{naslov}: {datum} - {red['vrsta']} - {_novcani_prikaz(red['iznos'])}"
    if tabela == "gume":
        return f"{naslov}: {datum} - {red['sezona']} {red['marka'] or ''} {red['model'] or ''}".strip()
    if tabela == "registracija":
        return f"{naslov}: {datum} - istice {red['istek'] or '-'}"
    if tabela == "osiguranje":
        return f"{naslov}: {datum} - istice {red['istek'] or '-'}"
    if tabela == "akumulator":
        return f"{naslov}: {datum} - {red['marka'] or ''} {red['model'] or ''}".strip()
    if tabela == "kvarovi":
        return f"{naslov}: {datum} - {_novcani_prikaz(red['ukupna_cena'])}"
    if tabela == "dokumenti":
        return f"{naslov}: {datum} - {red['tip']} {red['naziv'] or ''}".strip()
    if tabela == "podsetnici":
        return f"{naslov}: {datum} - {red['naslov'] or red['tip']}"
    return f"{naslov}: {datum}"


class HistoryScreen(Screen):
    """
    Istorija svih zapisa - organizovano po vozilu. Prikazuje vozila;
    klik na vozilo otvara SVE zapise tog vozila iz svih kategorija
    (gorivo, servisi, troskovi, gume, registracija, osiguranje,
    akumulator, kvarovi, dokumenta, podsetnici), sortirano po datumu.
    """

    def on_pre_enter(self, *args):
        self.ids.title_label.text = "Istorija svih zapisa"
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
            broj_zapisa = sum(
                len(db.get_by_vehicle(tabela, vozilo["id"])) for tabela in SVE_TABELE
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

    # ---------- Nivo 1: svi zapisi jednog vozila (sve kategorije) ----------

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
            title="Svi zapisi vozila", content=content, size_hint=(0.92, 0.85),
            overlay_color=(0, 0, 0, 0.85),
        )

        def refresh_records():
            records_box.clear_widgets()

            svi = []
            for tabela in SVE_TABELE:
                for red in db.get_by_vehicle(tabela, vehicle_id):
                    svi.append((tabela, red))

            svi.sort(key=lambda par: par[1][DATUM_POLJE[par[0]]] or "", reverse=True)

            if not svi:
                popup.dismiss()
                self.load_history()
                return

            for tabela, red in svi:
                btn = SecondaryButton(
                    text=_kratak_opis(tabela, red),
                    size_hint_y=None, height=dp(56), halign="center",
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

    # ---------- Nivo 2: detalji jednog zapisa (generieno, sve kolone) ----------

    def open_record_detail(self, tabela, record_id, parent_popup, refresh_parent):
        red = db.get_by_id(tabela, record_id)
        if red is None:
            return

        content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(
            Label(text=NASLOVI[tabela], bold=True, font_size="16sp",
                  size_hint_y=None, height=dp(28))
        )

        for kljuc in red.keys():
            if kljuc in ("id", "vehicle_id"):
                continue
            vrednost = red[kljuc]
            if vrednost in (None, ""):
                continue
            content.add_widget(
                Label(text=f"{kljuc}: {vrednost}", size_hint_y=None, height=dp(26),
                      halign="left")
            )

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(content)

        outer = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        outer.add_widget(scroll)

        detail_popup = Popup(
            title="Detalji zapisa", content=outer, size_hint=(0.9, 0.75),
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
        outer.add_widget(btn_row)

        detail_popup.open()

    def go_back(self):
        self.manager.current = "home"

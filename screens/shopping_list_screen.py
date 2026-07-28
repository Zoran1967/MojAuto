import os
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image as KivyImage
from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput, Card
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.app import App
from kivy.utils import platform

from database import db
from translations import prevedi


def _jezik():
    return db.get_setting("jezik", "sr")


def _slika_putanja(oznaka):
    app = App.get_running_app()
    folder = app.user_data_dir
    return os.path.join(folder, f"cena_{oznaka}.jpg")


class ShoppingListScreen(Screen):
    """
    Ekran aktivnih lista za kupovinu.

    NAPOMENA (izmena po zahtevu - vise istovremenih lista): aplikacija
    sad podrzava VISE istovremeno otvorenih lista, po jednu po
    prodavnici (npr. kupovina istog dana i u Maxi-ju i u Lidl-u).
    Nema vise pojma "trenutna lista" (self.lista_id) - umesto toga,
    svaka prodavnica koja ima otvorenu (nezatvorenu) listu prikazuje se
    kao zasebna kartica na ovom ekranu, ucitano direktno iz baze
    (db.get_otvorene_liste()) svaki put kad se ekran otvori.

    Lista postaje deo istorije TEK kad korisnik pritisne "Snimi racun"
    na kartici te prodavnice (db.close_lista) - do tada ostaje otvorena
    i vidljiva ovde, cak i ako korisnik ode na drugi ekran i vrati se.

    add_product_to_current_list() je javna metoda koju koristi i ovaj
    ekran i DatabaseScreen (dugme "Dodaj u listu"). Ako se ne prosledi
    prodavnica_id, koristi se prva prodavnica u bazi.

    Napomena o valutama: cene se uvek cuvaju u RSD, prikaz preko
    db.rsd_u_prikaz(). Tekstovi se prevode preko prevedi().

    Napomena o kameri: funkcije za slikanje (slikaj_za_novi_proizvod,
    slikaj_za_postojeci_red i pomocne _otvori_kameru_popup i sl.) su
    OSTAVLJENE NETAKNUTE na izricit zahtev - trenutno nisu povezane
    na dugmad u novom UI-ju (nisu ni bile pouzdane), ali kod ostaje
    ovde netaknut za slucaj da se kasnije ponovo poveze.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._foto_brojac = 0

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.add_product_btn.text = prevedi("sl_add_product_btn", jezik)
        self.ids.grand_total_word.text = prevedi("sl_grand_total", jezik)
        self.load_open_lists()

    # ---------- Prikaz svih otvorenih lista (po prodavnici) ----------

    def load_open_lists(self):
        jezik = _jezik()
        box = self.ids.items_box
        box.clear_widgets()

        otvorene = db.get_otvorene_liste()
        grand_total_rsd = 0.0

        if not otvorene:
            box.add_widget(Label(
                text=prevedi("sl_no_open_lists", jezik),
                size_hint_y=None, height=dp(60), color=(0.75, 0.75, 0.75, 1),
            ))
        else:
            for lista_id, prodavnica_id, prodavnica_naziv in otvorene:
                subtotal_rsd = self._napravi_karticu_prodavnice(
                    box, lista_id, prodavnica_id, prodavnica_naziv
                )
                grand_total_rsd += subtotal_rsd

        self.ids.grand_total_label.text = f"{db.rsd_u_prikaz(grand_total_rsd):.2f} {db.valuta_oznaka()}"

    def _napravi_karticu_prodavnice(self, parent_box, lista_id, prodavnica_id, prodavnica_naziv):
        jezik = _jezik()
        card = Card(orientation="vertical", padding=dp(10), spacing=dp(6),
                    size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))

        header = Label(
            text=prodavnica_naziv, bold=True, font_size="16sp",
            size_hint_y=None, height=dp(28),
        )
        card.add_widget(header)

        col_header = BoxLayout(size_hint_y=None, height=dp(24))
        col_header.add_widget(Label(text=prevedi("sl_col_product", jezik), bold=True, font_size="12sp"))
        col_header.add_widget(Label(text=prevedi("sl_col_qty", jezik), bold=True, size_hint_x=0.4, font_size="12sp"))
        col_header.add_widget(Label(text=prevedi("sl_col_price", jezik), bold=True, size_hint_x=0.5, font_size="12sp"))
        col_header.add_widget(Label(text=prevedi("sl_col_total", jezik), bold=True, size_hint_x=0.5, font_size="12sp"))
        card.add_widget(col_header)

        stavke = db.get_stavke_sa_id(lista_id)
        subtotal_rsd = 0.0

        for stavka_id, naziv, kolicina, cena_rsd, total_rsd, proizvod_id in stavke:
            subtotal_rsd += total_rsd
            row = Button(
                text=(
                    f"{naziv}   {kolicina:g}   "
                    f"{db.rsd_u_prikaz(cena_rsd):.2f}   "
                    f"{db.rsd_u_prikaz(total_rsd):.2f}"
                ),
                size_hint_y=None, height=dp(40),
                background_normal="", background_color=(0.20, 0.20, 0.22, 1),
                color=(1, 1, 1, 1), font_size="13sp",
            )
            row.bind(
                on_release=lambda inst, sid=stavka_id, n=naziv, k=kolicina, c=cena_rsd,
                                  pid=prodavnica_id, pnaziv=prodavnica_naziv:
                    self.open_edit_item_popup(sid, n, k, c, pid, pnaziv)
            )
            card.add_widget(row)

        subtotal_label = Label(
            text=f"{prevedi('sl_total_label', jezik)} {db.rsd_u_prikaz(subtotal_rsd):.2f} {db.valuta_oznaka()}",
            bold=True, size_hint_y=None, height=dp(28),
        )
        card.add_widget(subtotal_label)

        snimi_btn = PrimaryButton(
            text=prevedi("sl_snimi_racun", jezik), size_hint_y=None, height=dp(44),
        )
        snimi_btn.bind(on_release=lambda inst: self.snimi_racun(lista_id, subtotal_rsd))
        card.add_widget(snimi_btn)

        parent_box.add_widget(card)
        return subtotal_rsd

    def snimi_racun(self, lista_id, ukupno_rsd):
        """Cuva listu u istoriju TEK sada (zahtev 9) - dok se ovo ne
        pritisne, lista NIJE deo istorije."""
        db.close_lista(lista_id, ukupno_rsd)
        self.load_open_lists()

    # ---------- Zajednicka logika dodavanja stavke (koristi i ovaj ekran i DatabaseScreen) ----------

    def add_product_to_current_list(self, naziv, jedinica, kolicina, cena_rsd, prodavnica_id=None):
        """
        Dodaje proizvod u otvorenu listu date prodavnice. Ako
        prodavnica_id nije prosledjen, koristi se prva prodavnica u
        bazi (default) - ovo koristi DatabaseScreen kad dodaje direktno
        iz baze proizvoda. Vraca True ako je uspelo, False ako ne
        postoji nijedna prodavnica u bazi.
        """
        if prodavnica_id is None:
            prva = db.get_prva_prodavnica()
            if prva is None:
                return False
            prodavnica_id = prva[0]

        lista_id = db.get_or_create_otvorena_lista(prodavnica_id)
        proizvod_id = db.add_or_update_proizvod(naziv, jedinica, cena_rsd, prodavnica_id)
        db.add_stavka(lista_id, proizvod_id, naziv, kolicina, cena_rsd)
        return True

    # ---------- Poruka (npr. "nema prodavnica") ----------

    def _prikazi_poruku(self, tekst):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(text=tekst))
        popup = Popup(title="", content=content, size_hint=(0.85, 0.35), overlay_color=(0, 0, 0, 0.85))
        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    # ---------- Izbor prodavnice (generican picker - koristi se i za dodavanje i za izmenu stavke) ----------

    def open_store_picker_popup(self, on_chosen):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        search = StyledTextInput(
            hint_text=prevedi("sl_search_store_hint", jezik),
            size_hint_y=None, height=dp(44), multiline=False,
        )
        content.add_widget(search)

        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        popup = Popup(
            title=prevedi("sl_pick_store_title", jezik), content=content,
            size_hint=(0.9, 0.75), auto_dismiss=False,
            overlay_color=(0, 0, 0, 0.85),
        )

        def choose(pid, naziv):
            on_chosen(pid, naziv)
            popup.dismiss()

        def refresh(*a):
            results_box.clear_widgets()
            query = search.text.strip().lower()
            for pid, naziv in db.get_prodavnice():
                if query in naziv.lower():
                    btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
                    btn.bind(on_release=lambda inst, pid=pid, naziv=naziv: choose(pid, naziv))
                    results_box.add_widget(btn)

        def add_new(*a):
            naziv = search.text.strip()
            if not naziv:
                return
            pid = db.add_prodavnica(naziv)
            choose(pid, naziv)

        search.bind(text=refresh)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text=prevedi("sl_add_store_btn", jezik))
        add_btn.bind(on_release=add_new)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        refresh()
        popup.open()

    # ---------- Dodavanje proizvoda (zahtev 5: default prva prodavnica, jednim klikom promeni) ----------

    def add_item(self):
        prva = db.get_prva_prodavnica()
        if prva is None:
            # Nema nijedne prodavnice - umesto da samo blokiramo porukom,
            # odmah otvaramo picker koji ima "+ Prodavnica" dugme za
            # dodavanje, pa nastavljamo direktno na dodavanje proizvoda.
            def posle_dodavanja_prodavnice(pid, naziv):
                self.open_add_item_popup(pid, naziv)
            self.open_store_picker_popup(posle_dodavanja_prodavnice)
            return
        self.open_add_item_popup(prva[0], prva[1])

    def open_add_item_popup(self, prodavnica_id, prodavnica_naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        store_state = {"id": prodavnica_id, "naziv": prodavnica_naziv}
        store_btn = SecondaryButton(
            text=prevedi("sl_store_label", jezik).format(naziv=prodavnica_naziv),
            size_hint_y=None, height=dp(44),
        )
        content.add_widget(store_btn)

        naziv_input = StyledTextInput(
            hint_text=prevedi("sl_product_name_hint", jezik), size_hint_y=None, height=dp(44), multiline=False,
        )
        content.add_widget(naziv_input)

        suggestions_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        suggestions_box.bind(minimum_height=suggestions_box.setter("height"))
        sugg_scroll = ScrollView(size_hint_y=None, height=dp(120))
        sugg_scroll.add_widget(suggestions_box)
        content.add_widget(sugg_scroll)

        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        jedinica_input = StyledTextInput(hint_text=prevedi("sl_unit_hint", jezik), multiline=False)
        kolicina_input = StyledTextInput(hint_text=prevedi("sl_qty_hint", jezik), input_filter="float", multiline=False)
        cena_input = StyledTextInput(
            hint_text=prevedi("sl_price_hint", jezik).format(valuta=db.valuta_oznaka()),
            input_filter="float", multiline=False,
        )
        row.add_widget(jedinica_input)
        row.add_widget(kolicina_input)
        row.add_widget(cena_input)
        content.add_widget(row)

        total_label = Label(
            text=prevedi("sl_total_prefix", jezik).format(total="0.00", valuta=db.valuta_oznaka()),
            size_hint_y=None, height=dp(30),
        )
        content.add_widget(total_label)

        def update_total(*a):
            try:
                k = float(kolicina_input.text.replace(",", "."))
                c = float(cena_input.text.replace(",", "."))
                total_label.text = prevedi("sl_total_prefix", jezik).format(total=f"{k * c:.2f}", valuta=db.valuta_oznaka())
            except ValueError:
                total_label.text = prevedi("sl_total_prefix", jezik).format(total="0.00", valuta=db.valuta_oznaka())

        kolicina_input.bind(text=update_total)
        cena_input.bind(text=update_total)

        def pick_suggestion(naziv, jedinica, cena_rsd):
            naziv_input.unbind(text=refresh_suggestions)
            naziv_input.text = naziv
            naziv_input.bind(text=refresh_suggestions)
            jedinica_input.text = jedinica
            cena_input.text = f"{db.rsd_u_prikaz(cena_rsd):.2f}"
            update_total()
            suggestions_box.clear_widgets()

        def refresh_suggestions(*a):
            suggestions_box.clear_widgets()
            query = naziv_input.text.strip().lower()
            if not query:
                return
            for pid, naziv, jedinica, cena_rsd in db.search_proizvodi(query):
                cena_prikaz = db.rsd_u_prikaz(cena_rsd)
                btn = SecondaryButton(
                    text=f"{naziv}  ({jedinica}, {cena_prikaz:.2f} {db.valuta_oznaka()})",
                    size_hint_y=None, height=dp(36),
                )
                btn.bind(
                    on_release=lambda inst, n=naziv, j=jedinica, c=cena_rsd: pick_suggestion(n, j, c)
                )
                suggestions_box.add_widget(btn)

        naziv_input.bind(text=refresh_suggestions)

        def on_store_chosen(pid, pnaziv):
            store_state["id"] = pid
            store_state["naziv"] = pnaziv
            store_btn.text = prevedi("sl_store_label", jezik).format(naziv=pnaziv)

        store_btn.bind(on_release=lambda inst: self.open_store_picker_popup(on_store_chosen))

        btn_row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text=prevedi("sl_add_to_list_btn", jezik))
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        btn_row2.add_widget(add_btn)
        btn_row2.add_widget(cancel_btn)
        content.add_widget(btn_row2)

        popup = Popup(
            title=prevedi("sl_add_item_title", jezik), content=content, size_hint=(0.9, 0.9),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )
        cancel_btn.bind(on_release=popup.dismiss)

        def confirm(*a):
            naziv = naziv_input.text.strip()
            jedinica = jedinica_input.text.strip() or "kom"

            if not naziv:
                return
            try:
                kolicina = float(kolicina_input.text.replace(",", "."))
                cena_prikaz = float(cena_input.text.replace(",", "."))
            except ValueError:
                return
            if kolicina <= 0 or cena_prikaz < 0:
                return

            cena_rsd = db.prikaz_u_rsd(cena_prikaz)
            self.add_product_to_current_list(naziv, jedinica, kolicina, cena_rsd, store_state["id"])
            popup.dismiss()
            self.load_open_lists()

        add_btn.bind(on_release=confirm)
        popup.open()

    # ---------- Izmena/brisanje/pomeranje pojedinacne stavke (zahtev 6) ----------

    def open_edit_item_popup(self, stavka_id, naziv, kolicina, cena_rsd, prodavnica_id, prodavnica_naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        content.add_widget(
            Label(text=naziv, bold=True, font_size="16sp", size_hint_y=None, height=dp(30))
        )

        row1 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        kolicina_input = StyledTextInput(text=f"{kolicina:g}", input_filter="float", multiline=False)
        row1.add_widget(Label(text=prevedi("sl_qty_hint", jezik), size_hint_x=0.4))
        row1.add_widget(kolicina_input)
        content.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        cena_input = StyledTextInput(
            text=f"{db.rsd_u_prikaz(cena_rsd):.2f}", input_filter="float", multiline=False
        )
        row2.add_widget(Label(
            text=prevedi("sl_price_hint", jezik).format(valuta=db.valuta_oznaka()), size_hint_x=0.4
        ))
        row2.add_widget(cena_input)
        content.add_widget(row2)

        store_state = {"id": prodavnica_id, "naziv": prodavnica_naziv}
        store_btn = SecondaryButton(
            text=prevedi("sl_change_store_btn", jezik).format(naziv=prodavnica_naziv),
            size_hint_y=None, height=dp(44),
        )
        content.add_widget(store_btn)

        def on_store_chosen(pid, pnaziv):
            store_state["id"] = pid
            store_state["naziv"] = pnaziv
            store_btn.text = prevedi("sl_change_store_btn", jezik).format(naziv=pnaziv)

        store_btn.bind(on_release=lambda inst: self.open_store_picker_popup(on_store_chosen))

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("sl_item_edit_title", jezik), content=content, size_hint=(0.9, 0.8),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            try:
                nova_kolicina = float(kolicina_input.text.replace(",", "."))
                nova_cena_prikaz = float(cena_input.text.replace(",", "."))
            except ValueError:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return
            if nova_kolicina <= 0 or nova_cena_prikaz < 0:
                error_label.text = prevedi("db_err_negative_price", jezik)
                return
            nova_cena_rsd = db.prikaz_u_rsd(nova_cena_prikaz)

            if store_state["id"] != prodavnica_id:
                db.move_stavka_prodavnica(stavka_id, store_state["id"])

            db.update_stavka(stavka_id, nova_kolicina, nova_cena_rsd)
            popup.dismiss()
            self.load_open_lists()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("sl_confirm_delete_item", jezik)
                return
            # Brise SAMO stavku sa liste - proizvod u bazi ostaje netaknut
            # (zahtev: "brisanje sa liste ne sme obrisati proizvod iz baze proizvoda")
            db.delete_stavka(stavka_id)
            popup.dismiss()
            self.load_open_lists()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("sl_save", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(
            text=prevedi("sl_delete_item_btn", jezik), size_hint_y=None, height=dp(44),
        )
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    # ---------- Kamera (NETAKNUTO - ostavljeno kako je bilo, nije povezano na novi UI) ----------

    def _sledeca_foto_putanja(self):
        self._foto_brojac += 1
        return _slika_putanja(self._foto_brojac)

    def _zatrazi_dozvolu_pa_otvori_kameru(self, na_snimljeno=None):
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission, check_permission

                if check_permission(Permission.CAMERA):
                    self._otvori_kameru_popup(na_snimljeno)
                    return

                def callback(permissions, results):
                    if all(results):
                        from kivy.clock import Clock
                        Clock.schedule_once(lambda dt: self._otvori_kameru_popup(na_snimljeno), 0)
                    else:
                        self._prikazi_gresku_dozvole()

                request_permissions([Permission.CAMERA], callback)
                return
            except Exception:
                pass

        self._otvori_kameru_popup(na_snimljeno)

    def _prikazi_gresku_dozvole(self):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(text="Dozvola za kameru nije odobrena.\nProveri Podesavanja telefona -> Aplikacije -> Shoping -> Dozvole."))
        popup = Popup(title="Kamera", content=content, size_hint=(0.85, 0.4))
        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def _otvori_kameru_popup(self, na_snimljeno=None):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        try:
            cam_widget = Camera(play=True, resolution=(640, 480))
        except Exception:
            content.add_widget(Label(text="Kamera nije dostupna na ovom uredjaju."))
            popup = Popup(title="Kamera", content=content, size_hint=(0.9, 0.7))
            close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
            close_btn.bind(on_release=popup.dismiss)
            content.add_widget(close_btn)
            popup.open()
            return

        content.add_widget(cam_widget)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        snimi_btn = PrimaryButton(text="Snimi")
        otkazi_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        btn_row.add_widget(snimi_btn)
        btn_row.add_widget(otkazi_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title="Slikaj cenu", content=content, size_hint=(0.95, 0.9),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )
        otkazi_btn.bind(on_release=lambda inst: (setattr(cam_widget, "play", False), popup.dismiss()))

        def snimi(*a):
            putanja = self._sledeca_foto_putanja()
            try:
                cam_widget.export_to_png(putanja)
            except Exception:
                return
            cam_widget.play = False
            popup.dismiss()
            self._pokazi_snimljenu_sliku(putanja, na_snimljeno)

        snimi_btn.bind(on_release=snimi)
        popup.open()

    def _pokazi_snimljenu_sliku(self, putanja_slike, na_snimljeno=None):
        jezik = _jezik()
        if not putanja_slike or not os.path.exists(putanja_slike):
            return
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        img = KivyImage(source=putanja_slike, allow_stretch=True, keep_ratio=True)
        content.add_widget(img)
        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        content.add_widget(close_btn)
        popup = Popup(title="Foto", content=content, size_hint=(0.92, 0.85), overlay_color=(0, 0, 0, 0.85))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
        if na_snimljeno:
            na_snimljeno(putanja_slike)

    def slikaj_za_novi_proizvod(self, cena_input_widget):
        self._zatrazi_dozvolu_pa_otvori_kameru()

    def slikaj_za_postojeci_red(self, naziv_proizvoda):
        self._zatrazi_dozvolu_pa_otvori_kameru()

    # ---------- Navigacija ----------

    def go_back(self):
        self.manager.current = "home"

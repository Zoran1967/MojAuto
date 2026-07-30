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
from translations import prevedi


def _jezik():
    return db.get_setting("jezik", "sr")


class _IconButton(ButtonBehavior, KivyImage):
    """Mala slika koja se ponasa kao dugme (npr. olovka za izmenu
    proizvoda unutar grupe)."""
    pass


class DatabaseScreen(Screen):
    """
    Ekran za pregled sacuvanih proizvoda, prodavnica i kategorija.
    Tri taba: Proizvodi, Prodavnice, Kategorije.

    Napomena o valutama: cene u bazi su UVEK u RSD. Ovde se prikazuju
    i unose preko db.rsd_u_prikaz() / db.prikaz_u_rsd().
    Tekstovi se prevode preko prevedi() prema trenutno izabranom jeziku.

    Napomena o kategorijama: svaki proizvod moze imati kategoriju i
    podkategoriju (birane iz baze kategorije). Korisnik moze dodavati,
    menjati i brisati svoje kategorije i podkategorije u tabu
    "Kategorije" - brisanje je zasticeno (ne moze se obrisati kategorija
    koja ima podkategorije ili je u upotrebi kod nekog proizvoda).

    Napomena o "Dodaj u listu": ne postoji vise pojam jedne "trenutne"
    liste - dodaj_u_listu koristi izabranu prodavnicu (podrazumevano
    prva prodavnica u bazi) - isto pravilo kao i na ekranu Liste za
    kupovinu.

    NOVO - grupisani prikaz proizvoda (tab "Proizvodi"): umesto jedne
    velike liste svih proizvoda, prvo se prikazuju samo GLAVNE
    kategorije (grupe). Klikom na grupu otvara se lista proizvoda iz
    te grupe, sa poljem za kolicinu i cenu odmah pored svakog
    proizvoda i dugmetom za brzo dodavanje na listu za IZABRANU
    prodavnicu (cena se automatski predlaze prema poslednjoj
    zabelezenoj ceni ZA TU prodavnicu - db.get_cena_za_prodavnicu).
    Postojeca funkcija za izmenu/brisanje pojedinacnog proizvoda
    (open_edit_popup) ostaje potpuno ista, samo se sada otvara iz
    liste proizvoda unutar grupe (dugme "izmeni") umesto iz stare
    ravne liste.
    """

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.title_label.text = prevedi("db_title", jezik)
        self.ids.tab_products.text = prevedi("db_tab_products", jezik)
        self.ids.tab_stores.text = prevedi("db_tab_stores", jezik)
        self.ids.tab_categories.text = prevedi("db_tab_categories", jezik)
        # Uvek pocinjemo od pregleda grupa (ne ostajemo "duboko" u
        # nekoj grupi kad se korisnik vrati na ovaj ekran).
        self._trenutna_kategorija = None
        self.show_proizvodi()

    # =========================================================
    # TAB: Proizvodi (grupe -> proizvodi unutar grupe)
    # =========================================================

    def show_proizvodi(self):
        """Prikazuje SAMO glavne grupe (kategorije). Ovo je pocetni
        prikaz taba 'Proizvodi' - vise nema velike ravne liste svih
        proizvoda."""
        jezik = _jezik()
        self._trenutna_kategorija = None
        box = self.ids.database_box
        box.clear_widgets()

        kategorije = db.get_kategorije(roditelj_id=None)
        if not kategorije:
            box.add_widget(Label(
                text=prevedi("db_categories_empty", jezik), size_hint_y=None,
                height=dp(40), color=(1, 1, 1, 1),
            ))
            return

        for kid, naziv in kategorije:
            btn = Button(
                text=naziv, size_hint_y=None, height=dp(46),
                background_normal="", background_color=(0.18, 0.18, 0.22, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(
                on_release=lambda inst, kid=kid, naziv=naziv:
                    self.show_proizvodi_iz_kategorije(kid, naziv)
            )
            box.add_widget(btn)

    def show_proizvodi_iz_kategorije(self, kategorija_id, kategorija_naziv):
        """Prikazuje sve proizvode iz JEDNE glavne kategorije, svaki sa
        poljem za kolicinu i cenu i dugmetom za dodavanje na listu."""
        jezik = _jezik()
        self._trenutna_kategorija = {"id": kategorija_id, "naziv": kategorija_naziv}
        if not hasattr(self, "_izabrana_prodavnica"):
            self._izabrana_prodavnica = None
        if self._izabrana_prodavnica is None:
            prva = db.get_prva_prodavnica()
            if prva:
                self._izabrana_prodavnica = {"id": prva[0], "naziv": prva[1]}

        box = self.ids.database_box
        box.clear_widgets()

        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        nazad_btn = SecondaryButton(text=prevedi("db_back_to_categories", jezik), size_hint_x=0.4)
        nazad_btn.bind(on_release=lambda inst: self.show_proizvodi())
        header.add_widget(nazad_btn)

        prodavnica_stanje = self._izabrana_prodavnica
        prodavnica_tekst = prodavnica_stanje["naziv"] if prodavnica_stanje else prevedi("db_no_store", jezik)
        prodavnica_btn = SecondaryButton(text=prodavnica_tekst)

        def on_prodavnica_izabrana(pid, pnaziv):
            if pid is None:
                return
            self._izabrana_prodavnica = {"id": pid, "naziv": pnaziv}
            self.show_proizvodi_iz_kategorije(kategorija_id, kategorija_naziv)

        prodavnica_btn.bind(
            on_release=lambda inst: self.open_store_pick_popup(on_prodavnica_izabrana)
        )
        header.add_widget(prodavnica_btn)
        box.add_widget(header)

        naslov = Label(
            text=kategorija_naziv, bold=True, font_size="18sp",
            size_hint_y=None, height=dp(34), color=(1, 1, 1, 1),
        )
        box.add_widget(naslov)

        proizvodi = db.get_proizvodi_po_kategoriji(kategorija_id)
        if not proizvodi:
            box.add_widget(Label(
                text=prevedi("db_empty_products", jezik), size_hint_y=None,
                height=dp(40), color=(1, 1, 1, 1),
            ))
            return

        prodavnica_id = prodavnica_stanje["id"] if prodavnica_stanje else None

        for proizvod_id, naziv, jedinica, zadnja_cena_rsd in proizvodi:
            box.add_widget(
                self._napravi_red_proizvoda(
                    proizvod_id, naziv, jedinica, zadnja_cena_rsd,
                    kategorija_id, prodavnica_id,
                )
            )

    def _napravi_red_proizvoda(self, proizvod_id, naziv, jedinica, zadnja_cena_rsd,
                                kategorija_id, prodavnica_id):
        """Jedan red u prikazu proizvoda unutar grupe: naziv, polje za
        kolicinu, polje za cenu (predlozena poslednja cena ZA IZABRANU
        prodavnicu ako postoji), dugme za dodavanje na listu i dugme za
        izmenu/brisanje (otvara postojeci open_edit_popup)."""
        jezik = _jezik()

        red = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(74),
                         spacing=dp(2), padding=(0, dp(4)))

        gornji = BoxLayout(size_hint_y=None, height=dp(30))
        naziv_label = Label(
            text=f"{naziv} ({jedinica})", halign="left", valign="middle",
            color=(1, 1, 1, 1),
        )
        naziv_label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        gornji.add_widget(naziv_label)
        red.add_widget(gornji)

        donji = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(4))

        cena_za_prodavnicu = None
        if prodavnica_id is not None:
            cena_za_prodavnicu = db.get_cena_za_prodavnicu(proizvod_id, prodavnica_id)
        predlozena_cena_rsd = cena_za_prodavnicu if cena_za_prodavnicu is not None else zadnja_cena_rsd

        kolicina_input = StyledTextInput(
            hint_text=prevedi("db_qty_hint", jezik), input_filter="float",
            multiline=False, size_hint_x=0.28,
        )
        cena_input = StyledTextInput(
            text=(f"{db.rsd_u_prikaz(predlozena_cena_rsd):.2f}" if predlozena_cena_rsd else ""),
            hint_text=prevedi("db_label_price", jezik).format(valuta=db.valuta_oznaka()),
            input_filter="float", multiline=False, size_hint_x=0.32,
        )

        dodaj_btn = PrimaryButton(text="+", size_hint_x=0.18)
        izmeni_btn = _IconButton(
            source=App.get_running_app().assets_dir + "olovka.png",
            allow_stretch=True, keep_ratio=True, size_hint_x=0.18,
        )

        def dodaj(*a):
            if prodavnica_id is None:
                self._prikazi_kratku_poruku(prevedi("sl_no_stores_yet", jezik))
                return
            try:
                kolicina = float(kolicina_input.text.replace(",", "."))
            except ValueError:
                self._prikazi_kratku_poruku(prevedi("db_err_bad_price", jezik))
                return
            if kolicina <= 0:
                self._prikazi_kratku_poruku(prevedi("db_err_bad_price", jezik))
                return
            try:
                cena_prikaz = float(cena_input.text.replace(",", ".")) if cena_input.text.strip() else 0
            except ValueError:
                self._prikazi_kratku_poruku(prevedi("db_err_bad_price", jezik))
                return
            if cena_prikaz < 0:
                self._prikazi_kratku_poruku(prevedi("db_err_negative_price", jezik))
                return

            cena_rsd = db.prikaz_u_rsd(cena_prikaz)
            sl_screen = self.manager.get_screen("shopping_list")
            sl_screen.add_product_to_current_list(
                naziv, jedinica, kolicina, cena_rsd, prodavnica_id,
                kategorija_id=kategorija_id,
            )
            kolicina_input.text = ""
            self._prikazi_kratku_poruku(prevedi("db_added_to_list_msg", jezik))

        dodaj_btn.bind(on_release=dodaj)

        def izmeni(*a):
            puno = db.get_proizvod_puno(proizvod_id)
            if not puno:
                return
            (pid, pnaziv, pjedinica, pcena, pprodavnica_naziv, pprodavnica_id,
             pkategorija_id, pkategorija_naziv, ppodkategorija_id, ppodkategorija_naziv,
             ppodrazumevana_kolicina) = puno
            self.open_edit_popup(
                pid, pnaziv, pjedinica, pcena, pprodavnica_id, pprodavnica_naziv,
                pkategorija_id, pkategorija_naziv, ppodkategorija_id, ppodkategorija_naziv,
                ppodrazumevana_kolicina,
            )

        izmeni_btn.bind(on_release=izmeni)

        donji.add_widget(kolicina_input)
        donji.add_widget(cena_input)
        donji.add_widget(dodaj_btn)
        donji.add_widget(izmeni_btn)
        red.add_widget(donji)

        return red

    def open_edit_popup(self, proizvod_id, naziv, jedinica, cena_rsd, prodavnica_id, prodavnica_naziv,
                         kategorija_id, kategorija_naziv, podkategorija_id, podkategorija_naziv,
                         podrazumevana_kolicina):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        scroll = ScrollView(size_hint_y=1)
        inner = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))
        scroll.add_widget(inner)
        content.add_widget(scroll)

        row0 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        naziv_input = StyledTextInput(text=naziv, multiline=False)
        row0.add_widget(Label(text=prevedi("db_label_name", jezik), size_hint_x=0.4))
        row0.add_widget(naziv_input)
        inner.add_widget(row0)

        row1 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        jedinica_input = StyledTextInput(text=jedinica, multiline=False)
        row1.add_widget(Label(text=prevedi("db_label_unit", jezik), size_hint_x=0.4))
        row1.add_widget(jedinica_input)
        inner.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        cena_input = StyledTextInput(
            text=(f"{db.rsd_u_prikaz(cena_rsd):.2f}" if cena_rsd else ""),
            hint_text=prevedi("db_label_price", jezik).format(valuta=db.valuta_oznaka()),
            input_filter="float", multiline=False
        )
        row2.add_widget(Label(text=prevedi("db_label_price", jezik).format(valuta=db.valuta_oznaka()), size_hint_x=0.4))
        row2.add_widget(cena_input)
        inner.add_widget(row2)

        prodavnica_state = {"id": prodavnica_id, "naziv": prodavnica_naziv}

        row3 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row3.add_widget(Label(text=prevedi("db_label_store", jezik), size_hint_x=0.4))
        store_btn = SecondaryButton(
            text=(prodavnica_naziv if prodavnica_id else prevedi("db_no_store", jezik))
        )
        row3.add_widget(store_btn)
        inner.add_widget(row3)

        def on_store_chosen(pid, pnaziv):
            prodavnica_state["id"] = pid
            prodavnica_state["naziv"] = pnaziv
            store_btn.text = pnaziv if pid else prevedi("db_no_store", jezik)

        store_btn.bind(on_release=lambda inst: self.open_store_pick_popup(on_store_chosen))

        # ---- Kategorija ----
        kategorija_state = {"id": kategorija_id, "naziv": kategorija_naziv}

        row_kat = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row_kat.add_widget(Label(text=prevedi("db_label_category", jezik), size_hint_x=0.4))
        kategorija_btn = SecondaryButton(
            text=(kategorija_naziv if kategorija_id else prevedi("db_no_category", jezik))
        )
        row_kat.add_widget(kategorija_btn)
        inner.add_widget(row_kat)

        # ---- Podkategorija ----
        podkategorija_state = {"id": podkategorija_id, "naziv": podkategorija_naziv}

        row_podkat = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row_podkat.add_widget(Label(text=prevedi("db_label_subcategory", jezik), size_hint_x=0.4))
        podkategorija_btn = SecondaryButton(
            text=(podkategorija_naziv if podkategorija_id else prevedi("db_no_category", jezik))
        )
        row_podkat.add_widget(podkategorija_btn)
        inner.add_widget(row_podkat)

        def on_kategorija_chosen(kid, knaziv):
            kategorija_state["id"] = kid
            kategorija_state["naziv"] = knaziv
            kategorija_btn.text = knaziv if kid else prevedi("db_no_category", jezik)
            # Promena glavne kategorije brise dotad izabranu podkategoriju
            # (podkategorija pripada tacno jednoj kategoriji)
            podkategorija_state["id"] = None
            podkategorija_state["naziv"] = None
            podkategorija_btn.text = prevedi("db_no_category", jezik)

        kategorija_btn.bind(
            on_release=lambda inst: self.open_kategorija_pick_popup(on_kategorija_chosen)
        )

        def on_podkategorija_chosen(kid, knaziv):
            podkategorija_state["id"] = kid
            podkategorija_state["naziv"] = knaziv
            podkategorija_btn.text = knaziv if kid else prevedi("db_no_category", jezik)

        def otvori_podkategoriju(inst):
            if kategorija_state["id"] is None:
                self._prikazi_kratku_poruku(prevedi("db_pick_subcategory_first_msg", jezik))
                return
            self.open_podkategorija_pick_popup(kategorija_state["id"], on_podkategorija_chosen)

        podkategorija_btn.bind(on_release=otvori_podkategoriju)

        row4 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        kolicina_input = StyledTextInput(
            text=(f"{podrazumevana_kolicina:g}" if podrazumevana_kolicina else ""),
            hint_text=prevedi("db_qty_hint", jezik),
            input_filter="float", multiline=False,
        )
        row4.add_widget(Label(text=prevedi("db_label_qty", jezik), size_hint_x=0.4))
        row4.add_widget(kolicina_input)
        inner.add_widget(row4)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        inner.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_edit_title", jezik), content=content, size_hint=(0.92, 0.92),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            novi_naziv = naziv_input.text.strip()
            nova_jedinica = jedinica_input.text.strip() or "kom"
            if not novi_naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return

            cena_tekst = cena_input.text.strip()
            if cena_tekst:
                try:
                    nova_cena_prikaz = float(cena_tekst.replace(",", "."))
                except ValueError:
                    error_label.text = prevedi("db_err_bad_price", jezik)
                    return
                if nova_cena_prikaz < 0:
                    error_label.text = prevedi("db_err_negative_price", jezik)
                    return
            else:
                nova_cena_prikaz = 0

            kolicina_tekst = kolicina_input.text.strip()
            if kolicina_tekst:
                try:
                    nova_kolicina = float(kolicina_tekst.replace(",", "."))
                except ValueError:
                    nova_kolicina = None
            else:
                nova_kolicina = None

            nova_cena_rsd = db.prikaz_u_rsd(nova_cena_prikaz)

            uspeh = db.update_proizvod(
                proizvod_id, novi_naziv, nova_jedinica, nova_cena_rsd,
                prodavnica_state["id"], kategorija_state["id"], podkategorija_state["id"],
                nova_kolicina,
            )
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate", jezik)
                return

            popup.dismiss()
            if self._trenutna_kategorija:
                self.show_proizvodi_iz_kategorije(
                    self._trenutna_kategorija["id"], self._trenutna_kategorija["naziv"]
                )
            else:
                self.show_proizvodi()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("db_confirm_delete", jezik)
                return
            uspeh = db.delete_proizvod(proizvod_id)
            if not uspeh:
                error_label.text = prevedi("db_err_in_use", jezik)
                delete_state["confirm"] = False
                instance.text = prevedi("db_delete_product", jezik)
                return
            popup.dismiss()
            if self._trenutna_kategorija:
                self.show_proizvodi_iz_kategorije(
                    self._trenutna_kategorija["id"], self._trenutna_kategorija["naziv"]
                )
            else:
                self.show_proizvodi()

        def dodaj_u_listu(*a):
            sl_screen = self.manager.get_screen("shopping_list")
            try:
                kolicina = float(kolicina_input.text.replace(",", "."))
            except ValueError:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return
            if kolicina <= 0:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return

            uspeh = sl_screen.add_product_to_current_list(
                naziv_input.text.strip() or naziv,
                jedinica_input.text.strip() or jedinica,
                kolicina,
                cena_rsd,
            )
            if not uspeh:
                error_label.text = prevedi("sl_no_stores_yet", jezik)
                return
            popup.dismiss()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        add_to_list_btn = PrimaryButton(text=prevedi("db_add_to_list_btn", jezik), size_hint_y=None, height=dp(44))
        add_to_list_btn.bind(on_release=dodaj_u_listu)
        content.add_widget(add_to_list_btn)

        delete_btn = DangerButton(text=prevedi("db_delete_product", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    def _prikazi_kratku_poruku(self, tekst):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(Label(text=tekst))
        popup = Popup(title="", content=content, size_hint=(0.8, 0.3), overlay_color=(0, 0, 0, 0.85))
        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(44))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def open_store_pick_popup(self, on_chosen):
        """Picker za izbor prodavnice - koristi se iz open_edit_popup.
        Sad ima i polje za direktno dodavanje nove prodavnice (da ne bude
        cor sokak kad lista jos nema nijednu)."""
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        naziv_input = StyledTextInput(
            hint_text=prevedi("sl_search_store_hint", jezik),
            size_hint_y=None, height=dp(44), multiline=False,
        )
        content.add_widget(naziv_input)

        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        pick_popup = Popup(
            title=prevedi("db_pick_store_title", jezik), content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def choose(pid, naziv):
            on_chosen(pid, naziv)
            pick_popup.dismiss()

        def refresh_results(*a):
            results_box.clear_widgets()
            query = naziv_input.text.strip().lower()
            no_store_btn = SecondaryButton(
                text=prevedi("db_no_store", jezik), size_hint_y=None, height=dp(44)
            )
            no_store_btn.bind(on_release=lambda inst: choose(None, ""))
            results_box.add_widget(no_store_btn)
            for pid, naziv in db.get_prodavnice():
                if query in naziv.lower():
                    btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
                    btn.bind(on_release=lambda inst, pid=pid, naziv=naziv: choose(pid, naziv))
                    results_box.add_widget(btn)

        naziv_input.bind(text=refresh_results)

        def dodaj_novu(*a):
            naziv = naziv_input.text.strip()
            if not naziv:
                return
            pid = db.add_prodavnica(naziv)
            choose(pid, naziv)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text=prevedi("sl_add_store_btn", jezik))
        add_btn.bind(on_release=dodaj_novu)
        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        close_btn.bind(on_release=pick_popup.dismiss)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(close_btn)
        content.add_widget(btn_row)

        refresh_results()

        pick_popup.open()

    def open_kategorija_pick_popup(self, on_chosen):
        """Picker za izbor GLAVNE kategorije - koristi se iz open_edit_popup."""
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        pick_popup = Popup(
            title=prevedi("db_pick_category_title", jezik), content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def choose(kid, naziv):
            on_chosen(kid, naziv)
            pick_popup.dismiss()

        no_cat_btn = SecondaryButton(
            text=prevedi("db_no_category", jezik), size_hint_y=None, height=dp(44)
        )
        no_cat_btn.bind(on_release=lambda inst: choose(None, None))
        results_box.add_widget(no_cat_btn)

        kategorije = db.get_kategorije(roditelj_id=None)
        if not kategorije:
            results_box.add_widget(Label(
                text=prevedi("db_categories_empty", jezik), size_hint_y=None, height=dp(40)
            ))
        for kid, naziv in kategorije:
            btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
            btn.bind(on_release=lambda inst, kid=kid, naziv=naziv: choose(kid, naziv))
            results_box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=pick_popup.dismiss)
        content.add_widget(close_btn)

        pick_popup.open()

    def open_podkategorija_pick_popup(self, roditelj_kategorija_id, on_chosen):
        """Picker za izbor PODKATEGORIJE (unutar vec izabrane glavne kategorije)."""
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        pick_popup = Popup(
            title=prevedi("db_pick_subcategory_title", jezik), content=content, size_hint=(0.85, 0.8),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def choose(kid, naziv):
            on_chosen(kid, naziv)
            pick_popup.dismiss()

        no_cat_btn = SecondaryButton(
            text=prevedi("db_no_category", jezik), size_hint_y=None, height=dp(44)
        )
        no_cat_btn.bind(on_release=lambda inst: choose(None, None))
        results_box.add_widget(no_cat_btn)

        podkategorije = db.get_kategorije(roditelj_id=roditelj_kategorija_id)
        if not podkategorije:
            results_box.add_widget(Label(
                text=prevedi("db_subcategories_empty", jezik), size_hint_y=None, height=dp(40)
            ))
        for kid, naziv in podkategorije:
            btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
            btn.bind(on_release=lambda inst, kid=kid, naziv=naziv: choose(kid, naziv))
            results_box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=pick_popup.dismiss)
        content.add_widget(close_btn)

        pick_popup.open()

    # =========================================================
    # TAB: Prodavnice
    # =========================================================

    def show_prodavnice(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()

        novi_btn = PrimaryButton(
            text=prevedi("sl_add_store_btn", jezik), size_hint_y=None, height=dp(48),
        )
        novi_btn.bind(on_release=lambda inst: self.open_new_prodavnica_popup())
        box.add_widget(novi_btn)

        prodavnice = db.get_prodavnice()

        if not prodavnice:
            box.add_widget(
                Label(
                    text=prevedi("db_empty_stores", jezik),
                    size_hint_y=None, height=dp(40), color=(1, 1, 1, 1),
                )
            )
            return

        for pid, naziv in prodavnice:
            btn = Button(
                text=naziv, size_hint_y=None, height=dp(44),
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(
                on_release=lambda inst, pid=pid, naziv=naziv: self.open_edit_store_popup(pid, naziv)
            )
            box.add_widget(btn)

    def open_new_prodavnica_popup(self):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        naziv_input = StyledTextInput(
            hint_text=prevedi("db_label_store_name", jezik), multiline=False,
            size_hint_y=None, height=dp(44),
        )
        content.add_widget(naziv_input)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("sl_add_store_btn", jezik), content=content, size_hint=(0.85, 0.4),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def dodaj(*a):
            naziv = naziv_input.text.strip()
            if not naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            db.add_prodavnica(naziv)
            popup.dismiss()
            self.show_prodavnice()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=dodaj)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup.open()

    def open_edit_store_popup(self, prodavnica_id, naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        row0 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        naziv_input = StyledTextInput(text=naziv, multiline=False)
        row0.add_widget(Label(text=prevedi("db_label_store_name", jezik), size_hint_x=0.5))
        row0.add_widget(naziv_input)
        content.add_widget(row0)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_edit_store_title", jezik), content=content, size_hint=(0.9, 0.55),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            novi_naziv = naziv_input.text.strip()
            if not novi_naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            uspeh = db.update_prodavnica(prodavnica_id, novi_naziv)
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate_store", jezik)
                return
            popup.dismiss()
            self.show_prodavnice()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("db_confirm_delete_store", jezik)
                return
            uspeh = db.delete_prodavnica(prodavnica_id)
            if not uspeh:
                error_label.text = prevedi("db_err_store_in_use", jezik)
                delete_state["confirm"] = False
                instance.text = prevedi("db_delete_store", jezik)
                return
            popup.dismiss()
            self.show_prodavnice()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text=prevedi("db_delete_store", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    # =========================================================
    # TAB: Kategorije (CRUD glavnih kategorija i podkategorija)
    # =========================================================

    def show_kategorije(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()

        novi_btn = PrimaryButton(
            text=prevedi("db_new_category_btn", jezik), size_hint_y=None, height=dp(48),
        )
        novi_btn.bind(on_release=lambda inst: self.open_new_kategorija_popup())
        box.add_widget(novi_btn)

        kategorije = db.get_kategorije(roditelj_id=None)
        if not kategorije:
            box.add_widget(Label(
                text=prevedi("db_categories_empty", jezik), size_hint_y=None,
                height=dp(40), color=(1, 1, 1, 1),
            ))
            return

        for kid, naziv in kategorije:
            btn = Button(
                text=naziv, size_hint_y=None, height=dp(44),
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(
                on_release=lambda inst, kid=kid, naziv=naziv: self.open_kategorija_detail_popup(kid, naziv)
            )
            box.add_widget(btn)

    def open_new_kategorija_popup(self):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        naziv_input = StyledTextInput(
            hint_text=prevedi("db_edit_category_name", jezik), multiline=False,
            size_hint_y=None, height=dp(44),
        )
        content.add_widget(naziv_input)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_new_category_btn", jezik), content=content, size_hint=(0.85, 0.4),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def dodaj(*a):
            naziv = naziv_input.text.strip()
            if not naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            postojece = [n for _, n in db.get_kategorije(roditelj_id=None)]
            if naziv.lower() in [n.lower() for n in postojece]:
                error_label.text = prevedi("db_err_duplicate_category", jezik)
                return
            db.add_kategorija(naziv, roditelj_id=None)
            popup.dismiss()
            self.show_kategorije()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=dodaj)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup.open()

    def open_kategorija_detail_popup(self, kategorija_id, naziv):
        """Prikazuje podkategorije jedne glavne kategorije + opcije za
        izmenu naziva/brisanje same kategorije."""
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        content.add_widget(Label(text=naziv, bold=True, font_size="18sp",
                                  size_hint_y=None, height=dp(32)))

        sub_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        sub_box.bind(minimum_height=sub_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(sub_box)
        content.add_widget(scroll)

        detail_popup = Popup(
            title=prevedi("db_category_title", jezik), content=content, size_hint=(0.92, 0.85),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def refresh_sub():
            sub_box.clear_widgets()
            podkategorije = db.get_kategorije(roditelj_id=kategorija_id)
            if not podkategorije:
                sub_box.add_widget(Label(
                    text=prevedi("db_subcategories_empty", jezik),
                    size_hint_y=None, height=dp(36), color=(0.75, 0.75, 0.75, 1),
                ))
            for skid, sknaziv in podkategorije:
                btn = SecondaryButton(text=sknaziv, size_hint_y=None, height=dp(40))
                btn.bind(
                    on_release=lambda inst, skid=skid, sknaziv=sknaziv:
                        self.open_edit_subkategorija_popup(skid, sknaziv, kategorija_id, refresh_sub)
                )
                sub_box.add_widget(btn)

        refresh_sub()

        novi_sub_btn = PrimaryButton(
            text=prevedi("db_new_subcategory_btn", jezik), size_hint_y=None, height=dp(44),
        )
        novi_sub_btn.bind(
            on_release=lambda inst: self.open_new_subkategorija_popup(kategorija_id, refresh_sub)
        )
        content.add_widget(novi_sub_btn)

        naziv_input = StyledTextInput(text=naziv, multiline=False, size_hint_y=None, height=dp(44))
        content.add_widget(Label(text=prevedi("db_edit_category_name", jezik), size_hint_y=None, height=dp(24)))
        content.add_widget(naziv_input)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        def save_name(*a):
            novi_naziv = naziv_input.text.strip()
            if not novi_naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            uspeh = db.update_kategorija(kategorija_id, novi_naziv)
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate_category", jezik)
                return
            detail_popup.dismiss()
            self.show_kategorije()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("db_confirm_delete_category", jezik)
                return
            uspeh = db.delete_kategorija(kategorija_id)
            if not uspeh:
                error_label.text = prevedi("db_err_category_in_use", jezik)
                delete_state["confirm"] = False
                instance.text = prevedi("db_delete_category", jezik)
                return
            detail_popup.dismiss()
            self.show_kategorije()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=save_name)
        close_btn = SecondaryButton(text=prevedi("hist_close", jezik))
        close_btn.bind(on_release=detail_popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(close_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text=prevedi("db_delete_category", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        detail_popup.open()

    def open_new_subkategorija_popup(self, roditelj_id, on_dodato):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        naziv_input = StyledTextInput(
            hint_text=prevedi("db_edit_subcategory_name", jezik), multiline=False,
            size_hint_y=None, height=dp(44),
        )
        content.add_widget(naziv_input)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_new_subcategory_btn", jezik), content=content, size_hint=(0.85, 0.4),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def dodaj(*a):
            naziv = naziv_input.text.strip()
            if not naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            postojece = [n for _, n in db.get_kategorije(roditelj_id=roditelj_id)]
            if naziv.lower() in [n.lower() for n in postojece]:
                error_label.text = prevedi("db_err_duplicate_category", jezik)
                return
            db.add_kategorija(naziv, roditelj_id=roditelj_id)
            popup.dismiss()
            on_dodato()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=dodaj)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup.open()

    def open_edit_subkategorija_popup(self, subkategorija_id, naziv, roditelj_id, on_izmenjeno):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        naziv_input = StyledTextInput(text=naziv, multiline=False, size_hint_y=None, height=dp(44))
        content.add_widget(Label(text=prevedi("db_edit_subcategory_name", jezik), size_hint_y=None, height=dp(24)))
        content.add_widget(naziv_input)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_edit_subcategory_title", jezik), content=content, size_hint=(0.85, 0.5),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            novi_naziv = naziv_input.text.strip()
            if not novi_naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            uspeh = db.update_kategorija(subkategorija_id, novi_naziv)
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate_category", jezik)
                return
            popup.dismiss()
            on_izmenjeno()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("db_confirm_delete_category", jezik)
                return
            uspeh = db.delete_kategorija(subkategorija_id)
            if not uspeh:
                error_label.text = prevedi("db_err_category_in_use", jezik)
                delete_state["confirm"] = False
                instance.text = prevedi("db_delete_subcategory", jezik)
                return
            popup.dismiss()
            on_izmenjeno()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(
            text=prevedi("db_delete_subcategory", jezik), size_hint_y=None, height=dp(44),
        )
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    def go_back(self):
        self.manager.current = "home"

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, StyledTextInput
from translations import prevedi


def _jezik():
    return db.get_setting("jezik", "sr")


class DatabaseScreen(Screen):
    """
    Ekran za pregled sacuvanih proizvoda, prodavnica i kategorija.
    Napomena o valutama: cene u bazi su UVEK u RSD. Ovde se prikazuju
    i unose preko db.rsd_u_prikaz() / db.prikaz_u_rsd().
    Tekstovi se prevode preko prevedi() prema trenutno izabranom jeziku.

    Proizvodi (show_proizvodi) su grupisani po kategoriji, sa header
    redom za svaku kategoriju (i "Nekategorisano" na kraju za proizvode
    bez kategorije).

    Brisanje kategorije/potkategorije NIKAD ne brise proizvode - samo im
    postavlja kategorija_id/podkategorija_id na NULL (to je vec
    implementirano u database.py).
    """

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.title_label.text = prevedi("db_title", jezik)
        self.ids.tab_products.text = prevedi("db_tab_products", jezik)
        self.ids.tab_stores.text = prevedi("db_tab_stores", jezik)
        self.ids.tab_categories.text = prevedi("db_tab_categories", jezik)
        self.show_proizvodi()

    # ================= PROIZVODI (grupisano po kategoriji) =================

    def show_proizvodi(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()
        proizvodi = db.get_proizvodi_sa_prodavnicom()

        if not proizvodi:
            box.add_widget(
                Label(text=prevedi("db_empty_products", jezik), size_hint_y=None,
                      height=dp(40), color=(1, 1, 1, 1))
            )
            return

        header = BoxLayout(size_hint_y=None, height=dp(36))
        header.add_widget(Label(text=prevedi("db_col_product", jezik), bold=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text=prevedi("db_col_unit", jezik), bold=True, size_hint_x=0.3, color=(1, 1, 1, 1)))
        header.add_widget(Label(
            text=prevedi("db_col_price", jezik).format(valuta=db.valuta_oznaka()),
            bold=True, size_hint_x=0.4, color=(1, 1, 1, 1)
        ))
        box.add_widget(header)

        trenutna_kategorija = object()  # nikad jednako nicem na pocetku

        for (pid, naziv, jedinica, cena_rsd, prodavnica_naziv, prodavnica_id,
             kategorija_id, kategorija_naziv, podkategorija_id, podkategorija_naziv) in proizvodi:

            kategorija_kljuc = kategorija_id if kategorija_id else "NEKATEGORISANO"
            if kategorija_kljuc != trenutna_kategorija:
                trenutna_kategorija = kategorija_kljuc
                naslov = kategorija_naziv if kategorija_id else prevedi("db_uncategorized_header", jezik)
                kat_header = Label(
                    text=naslov, bold=True, size_hint_y=None, height=dp(30),
                    color=(0.6, 0.8, 1, 1),
                )
                box.add_widget(kat_header)

            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(2))

            def make_handler(pid=pid, naziv=naziv, jedinica=jedinica, cena_rsd=cena_rsd,
                              prodavnica_id=prodavnica_id, prodavnica_naziv=prodavnica_naziv,
                              kategorija_id=kategorija_id, kategorija_naziv=kategorija_naziv,
                              podkategorija_id=podkategorija_id, podkategorija_naziv=podkategorija_naziv):
                def handler(instance):
                    self.open_edit_popup(pid, naziv, jedinica, cena_rsd, prodavnica_id, prodavnica_naziv,
                                          kategorija_id, kategorija_naziv, podkategorija_id, podkategorija_naziv)
                return handler

            handler = make_handler()

            btn_naziv = Button(
                text=naziv, halign="left", valign="middle",
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
            )
            btn_naziv.bind(size=lambda inst, val: setattr(inst, "text_size", val))

            btn_jed = Button(
                text=jedinica, size_hint_x=0.3,
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
            )
            btn_cena = Button(
                text=f"{db.rsd_u_prikaz(cena_rsd):.2f}", size_hint_x=0.4,
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
            )

            btn_naziv.bind(on_release=handler)
            btn_jed.bind(on_release=handler)
            btn_cena.bind(on_release=handler)

            row.add_widget(btn_naziv)
            row.add_widget(btn_jed)
            row.add_widget(btn_cena)
            box.add_widget(row)

    def open_edit_popup(self, proizvod_id, naziv, jedinica, cena_rsd, prodavnica_id, prodavnica_naziv,
                         kategorija_id, kategorija_naziv, podkategorija_id, podkategorija_naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        scroll = ScrollView()
        inner = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))

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
            text=f"{db.rsd_u_prikaz(cena_rsd):.2f}", input_filter="float", multiline=False
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
        store_btn.bind(on_release=lambda inst: self.open_store_pick_popup(
            lambda pid, pnaziv: (
                prodavnica_state.update(id=pid, naziv=pnaziv),
                setattr(store_btn, "text", pnaziv if pid else prevedi("db_no_store", jezik)),
            )
        ))

        kategorija_state = {"id": kategorija_id, "naziv": kategorija_naziv,
                             "pod_id": podkategorija_id, "pod_naziv": podkategorija_naziv}

        row4 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row4.add_widget(Label(text=prevedi("db_label_category", jezik), size_hint_x=0.4))
        cat_btn = SecondaryButton(
            text=(kategorija_naziv if kategorija_id else prevedi("db_no_category", jezik))
        )
        row4.add_widget(cat_btn)
        inner.add_widget(row4)

        row5 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row5.add_widget(Label(text=prevedi("db_label_subcategory", jezik), size_hint_x=0.4))
        subcat_btn = SecondaryButton(
            text=(podkategorija_naziv if podkategorija_id else prevedi("db_no_subcategory", jezik))
        )
        row5.add_widget(subcat_btn)
        inner.add_widget(row5)

        def on_cat_chosen(kid, knaziv):
            kategorija_state["id"] = kid
            kategorija_state["naziv"] = kناziv if False else knaziv
            kategorija_state["pod_id"] = None
            kategorija_state["pod_naziv"] = ""
            cat_btn.text = knaziv if kid else prevedi("db_no_category", jezik)
            subcat_btn.text = prevedi("db_no_subcategory", jezik)

        cat_btn.bind(on_release=lambda inst: self.open_category_pick_popup(on_cat_chosen))

        def on_subcat_chosen(skid, snaziv):
            kategorija_state["pod_id"] = skid
            kategorija_state["pod_naziv"] = snaziv
            subcat_btn.text = snaziv if skid else prevedi("db_no_subcategory", jezik)

        def otvori_subcat(*a):
            if not kategorija_state["id"]:
                return
            self.open_subcategory_pick_popup(kategorija_state["id"], on_subcat_chosen)

        subcat_btn.bind(on_release=otvori_subcat)

        row6 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        kolicina_input = StyledTextInput(
            text="1", hint_text=prevedi("db_qty_hint", jezik),
            input_filter="float", multiline=False,
        )
        row6.add_widget(Label(text=prevedi("db_label_qty", jezik), size_hint_x=0.4))
        row6.add_widget(kolicina_input)
        inner.add_widget(row6)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        inner.add_widget(error_label)

        scroll.add_widget(inner)
        content.add_widget(scroll)

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
            try:
                nova_cena_prikaz = float(cena_input.text.replace(",", "."))
            except ValueError:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return
            if nova_cena_prikaz < 0:
                error_label.text = prevedi("db_err_negative_price", jezik)
                return

            nova_cena_rsd = db.prikaz_u_rsd(nova_cena_prikaz)

            uspeh = db.update_proizvod(
                proizvod_id, novi_naziv, nova_jedinica, nova_cena_rsd, prodavnica_state["id"],
                kategorija_state["id"], kategorija_state["pod_id"],
            )
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate", jezik)
                return

            popup.dismiss()
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
            self.show_proizvodi()

        def dodaj_u_listu(*a):
            sl_screen = self.manager.get_screen("shopping_list")
            if sl_screen.lista_id is None:
                error_label.text = prevedi("sl_no_active_list", jezik)
                return
            try:
                kolicina = float(kolicina_input.text.replace(",", "."))
            except ValueError:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return
            if kolicina <= 0:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return

            sl_screen.add_product_to_current_list(
                naziv_input.text.strip() or naziv,
                jedinica_input.text.strip() or jedinica,
                kolicina,
                cena_rsd,
            )
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

    def open_store_pick_popup(self, on_chosen):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        pick_popup = Popup(
            title=prevedi("db_pick_store_title", jezik), content=content, size_hint=(0.85, 0.7),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def choose(pid, naziv):
            on_chosen(pid, naziv)
            pick_popup.dismiss()

        no_store_btn = SecondaryButton(text=prevedi("db_no_store", jezik), size_hint_y=None, height=dp(44))
        no_store_btn.bind(on_release=lambda inst: choose(None, ""))
        results_box.add_widget(no_store_btn)

        for pid, naziv in db.get_prodavnice():
            btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
            btn.bind(on_release=lambda inst, pid=pid, naziv=naziv: choose(pid, naziv))
            results_box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=pick_popup.dismiss)
        content.add_widget(close_btn)

        pick_popup.open()

    def open_category_pick_popup(self, on_chosen):
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

        no_cat_btn = SecondaryButton(text=prevedi("db_no_category", jezik), size_hint_y=None, height=dp(44))
        no_cat_btn.bind(on_release=lambda inst: choose(None, ""))
        results_box.add_widget(no_cat_btn)

        for kid, naziv in db.get_kategorije():
            btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
            btn.bind(on_release=lambda inst, kid=kid, naziv=naziv: choose(kid, naziv))
            results_box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=pick_popup.dismiss)
        content.add_widget(close_btn)

        pick_popup.open()

    def open_subcategory_pick_popup(self, kategorija_id, on_chosen):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        pick_popup = Popup(
            title=prevedi("db_pick_subcategory_title", jezik), content=content, size_hint=(0.85, 0.7),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def choose(skid, naziv):
            on_chosen(skid, naziv)
            pick_popup.dismiss()

        no_sub_btn = SecondaryButton(text=prevedi("db_no_subcategory", jezik), size_hint_y=None, height=dp(44))
        no_sub_btn.bind(on_release=lambda inst: choose(None, ""))
        results_box.add_widget(no_sub_btn)

        podkategorije = db.get_podkategorije(kategorija_id)
        if not podkategorije:
            results_box.add_widget(
                Label(text=prevedi("db_empty_subcategories", jezik), size_hint_y=None,
                      height=dp(40), color=(0.7, 0.7, 0.7, 1))
            )
        for skid, naziv in podkategorije:
            btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
            btn.bind(on_release=lambda inst, skid=skid, naziv=naziv: choose(skid, naziv))
            results_box.add_widget(btn)

        close_btn = SecondaryButton(text=prevedi("sl_cancel", jezik), size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=pick_popup.dismiss)
        content.add_widget(close_btn)

        pick_popup.open()

    # ================= PRODAVNICE =================

    def show_prodavnice(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()
        prodavnice = db.get_prodavnice()

        if not prodavnice:
            box.add_widget(
                Label(text=prevedi("db_empty_stores", jezik), size_hint_y=None,
                      height=dp(40), color=(1, 1, 1, 1))
            )
            return

        for pid, naziv in prodavnice:
            btn = Button(
                text=naziv, size_hint_y=None, height=dp(44),
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda inst, pid=pid, naziv=naziv: self.open_edit_store_popup(pid, naziv))
            box.add_widget(btn)

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

    # ================= KATEGORIJE =================

    def show_kategorije(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()

        add_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        novi_naziv_input = StyledTextInput(hint_text=prevedi("db_add_category_hint", jezik), multiline=False)
        add_btn = PrimaryButton(text=prevedi("db_add_category_btn", jezik), size_hint_x=None, width=dp(120))

        def dodaj(*a):
            naziv = novi_naziv_input.text.strip()
            if not naziv:
                return
            db.add_kategorija(naziv)
            novi_naziv_input.text = ""
            self.show_kategorije()

        add_btn.bind(on_release=dodaj)
        add_row.add_widget(novi_naziv_input)
        add_row.add_widget(add_btn)
        box.add_widget(add_row)

        kategorije = db.get_kategorije()
        if not kategorije:
            box.add_widget(
                Label(text=prevedi("db_empty_categories", jezik), size_hint_y=None,
                      height=dp(40), color=(1, 1, 1, 1))
            )
            return

        for kid, naziv in kategorije:
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(4))
            btn = Button(
                text=naziv, background_normal="", background_color=(0.16, 0.16, 0.18, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda inst, kid=kid, naziv=naziv: self.open_edit_category_popup(kid, naziv))
            sub_btn = SecondaryButton(
                text=prevedi("db_manage_subcategories_btn", jezik), size_hint_x=None, width=dp(120)
            )
            sub_btn.bind(on_release=lambda inst, kid=kid, naziv=naziv: self.show_podkategorije(kid, naziv))
            row.add_widget(btn)
            row.add_widget(sub_btn)
            box.add_widget(row)

    def open_edit_category_popup(self, kategorija_id, naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        row0 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        naziv_input = StyledTextInput(text=naziv, multiline=False)
        row0.add_widget(Label(text=prevedi("db_label_category_name", jezik), size_hint_x=0.5))
        row0.add_widget(naziv_input)
        content.add_widget(row0)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_edit_category_title", jezik), content=content, size_hint=(0.9, 0.55),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            novi_naziv = naziv_input.text.strip()
            if not novi_naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            uspeh = db.update_kategorija(kategorija_id, novi_naziv)
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate_category", jezik)
                return
            popup.dismiss()
            self.show_kategorije()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("db_confirm_delete_category", jezik)
                return
            db.delete_kategorija(kategorija_id)
            popup.dismiss()
            self.show_kategorije()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text=prevedi("db_delete_category", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    def show_podkategorije(self, kategorija_id, kategorija_naziv):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()

        back_btn = SecondaryButton(
            text=prevedi("db_back_to_categories", jezik), size_hint_y=None, height=dp(40)
        )
        back_btn.bind(on_release=lambda inst: self.show_kategorije())
        box.add_widget(back_btn)

        naslov = Label(
            text=prevedi("db_subcategories_of", jezik).format(naziv=kategorija_naziv),
            bold=True, size_hint_y=None, height=dp(32), color=(1, 1, 1, 1),
        )
        box.add_widget(naslov)

        add_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        novi_naziv_input = StyledTextInput(hint_text=prevedi("db_add_subcategory_hint", jezik), multiline=False)
        add_btn = PrimaryButton(text=prevedi("db_add_subcategory_btn", jezik), size_hint_x=None, width=dp(130))

        def dodaj(*a):
            naziv = novi_naziv_input.text.strip()
            if not naziv:
                return
            db.add_podkategorija(naziv, kategorija_id)
            novi_naziv_input.text = ""
            self.show_podkategorije(kategorija_id, kategorija_naziv)

        add_btn.bind(on_release=dodaj)
        add_row.add_widget(novi_naziv_input)
        add_row.add_widget(add_btn)
        box.add_widget(add_row)

        podkategorije = db.get_podkategorije(kategorija_id)
        if not podkategorije:
            box.add_widget(
                Label(text=prevedi("db_empty_subcategories", jezik), size_hint_y=None,
                      height=dp(40), color=(1, 1, 1, 1))
            )
            return

        for skid, naziv in podkategorije:
            btn = Button(
                text=naziv, size_hint_y=None, height=dp(44),
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(
                on_release=lambda inst, skid=skid, naziv=naziv:
                    self.open_edit_subcategory_popup(skid, naziv, kategorija_id, kategorija_naziv)
            )
            box.add_widget(btn)

    def open_edit_subcategory_popup(self, podkategorija_id, naziv, kategorija_id, kategorija_naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        row0 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        naziv_input = StyledTextInput(text=naziv, multiline=False)
        row0.add_widget(Label(text=prevedi("db_label_subcategory_name", jezik), size_hint_x=0.5))
        row0.add_widget(naziv_input)
        content.add_widget(row0)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_edit_subcategory_title", jezik), content=content, size_hint=(0.9, 0.55),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def save(*a):
            novi_naziv = naziv_input.text.strip()
            if not novi_naziv:
                error_label.text = prevedi("db_err_empty_name", jezik)
                return
            uspeh = db.update_podkategorija(podkategorija_id, novi_naziv)
            if not uspeh:
                error_label.text = prevedi("db_err_duplicate_subcategory", jezik)
                return
            popup.dismiss()
            self.show_podkategorije(kategorija_id, kategorija_naziv)

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = prevedi("db_confirm_delete_subcategory", jezik)
                return
            db.delete_podkategorija(podkategorija_id)
            popup.dismiss()
            self.show_podkategorije(kategorija_id, kategorija_naziv)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text=prevedi("db_save", jezik))
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text=prevedi("db_delete_subcategory", jezik), size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    def go_back(self):
        self.manager.current = "home"

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
    Ekran za pregled sacuvanih proizvoda i prodavnica.
    Napomena o valutama: cene u bazi su UVEK u RSD. Ovde se prikazuju
    i unose preko db.rsd_u_prikaz() / db.prikaz_u_rsd().
    Tekstovi se prevode preko prevedi() prema trenutno izabranom jeziku.

    U popup-u za izmenu proizvoda sad postoji i dugme za izbor/promenu
    prodavnice (otvara mali picker sa spiskom svih prodavnica + opcija
    "Bez prodavnice"), pored postojeceg dugmeta "Dodaj u listu".
    """

    def on_pre_enter(self, *args):
        jezik = _jezik()
        self.ids.title_label.text = prevedi("db_title", jezik)
        self.ids.tab_products.text = prevedi("db_tab_products", jezik)
        self.ids.tab_stores.text = prevedi("db_tab_stores", jezik)
        self.show_proizvodi()

    def show_proizvodi(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()
        proizvodi = db.get_proizvodi_sa_prodavnicom()

        header = BoxLayout(size_hint_y=None, height=dp(36))
        header.add_widget(Label(text=prevedi("db_col_product", jezik), bold=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text=prevedi("db_col_unit", jezik), bold=True, size_hint_x=0.3, color=(1, 1, 1, 1)))
        header.add_widget(Label(
            text=prevedi("db_col_price", jezik).format(valuta=db.valuta_oznaka()),
            bold=True, size_hint_x=0.4, color=(1, 1, 1, 1)
        ))
        box.add_widget(header)

        if not proizvodi:
            box.add_widget(
                Label(text=prevedi("db_empty_products", jezik), size_hint_y=None,
                      height=dp(40), color=(1, 1, 1, 1))
            )
            return

        for pid, naziv, jedinica, cena_rsd, prodavnica_naziv, prodavnica_id in proizvodi:
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(2))

            def make_handler(pid=pid, naziv=naziv, jedinica=jedinica, cena_rsd=cena_rsd,
                              prodavnica_id=prodavnica_id, prodavnica_naziv=prodavnica_naziv):
                def handler(instance):
                    self.open_edit_popup(pid, naziv, jedinica, cena_rsd, prodavnica_id, prodavnica_naziv)
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

    def open_edit_popup(self, proizvod_id, naziv, jedinica, cena_rsd, prodavnica_id, prodavnica_naziv):
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        row0 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        naziv_input = StyledTextInput(text=naziv, multiline=False)
        row0.add_widget(Label(text=prevedi("db_label_name", jezik), size_hint_x=0.4))
        row0.add_widget(naziv_input)
        content.add_widget(row0)

        row1 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        jedinica_input = StyledTextInput(text=jedinica, multiline=False)
        row1.add_widget(Label(text=prevedi("db_label_unit", jezik), size_hint_x=0.4))
        row1.add_widget(jedinica_input)
        content.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        cena_input = StyledTextInput(
            text=f"{db.rsd_u_prikaz(cena_rsd):.2f}", input_filter="float", multiline=False
        )
        row2.add_widget(Label(text=prevedi("db_label_price", jezik).format(valuta=db.valuta_oznaka()), size_hint_x=0.4))
        row2.add_widget(cena_input)
        content.add_widget(row2)

        prodavnica_state = {"id": prodavnica_id, "naziv": prodavnica_naziv}

        row3 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row3.add_widget(Label(text=prevedi("db_label_store", jezik), size_hint_x=0.4))
        store_btn = SecondaryButton(
            text=(prodavnica_naziv if prodavnica_id else prevedi("db_no_store", jezik))
        )
        row3.add_widget(store_btn)
        content.add_widget(row3)

        def on_store_chosen(pid, pnaziv):
            prodavnica_state["id"] = pid
            prodavnica_state["naziv"] = pnaziv
            store_btn.text = pnaziv if pid else prevedi("db_no_store", jezik)

        store_btn.bind(on_release=lambda inst: self.open_store_pick_popup(on_store_chosen))

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(
            title=prevedi("db_edit_title", jezik), content=content, size_hint=(0.9, 0.85),
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
                proizvod_id, novi_naziv, nova_jedinica, nova_cena_rsd, prodavnica_state["id"]
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
            self.open_qty_popup(proizvod_id, naziv_input.text.strip() or naziv,
                                 jedinica_input.text.strip() or jedinica, cena_rsd, popup)

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
        """Mali picker za izbor prodavnice - koristi se iz open_edit_popup."""
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

        no_store_btn = SecondaryButton(
            text=prevedi("db_no_store", jezik), size_hint_y=None, height=dp(44)
        )
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

    def open_qty_popup(self, proizvod_id, naziv, jedinica, cena_rsd, parent_popup):
        """Mali popup koji trazi kolicinu, pa dodaje proizvod u aktivnu listu."""
        jezik = _jezik()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        qty_input = StyledTextInput(
            text="1", hint_text=prevedi("db_qty_hint", jezik),
            input_filter="float", multiline=False,
        )
        content.add_widget(qty_input)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        qty_popup = Popup(
            title=prevedi("db_qty_prompt_title", jezik), content=content, size_hint=(0.8, 0.4),
            overlay_color=(0, 0, 0, 0.85), auto_dismiss=False,
        )

        def confirm(*a):
            try:
                kolicina = float(qty_input.text.replace(",", "."))
            except ValueError:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return
            if kolicina <= 0:
                error_label.text = prevedi("db_err_bad_price", jezik)
                return

            sl_screen = self.manager.get_screen("shopping_list")
            sl_screen.add_product_to_current_list(naziv, jedinica, kolicina, cena_rsd)
            qty_popup.dismiss()
            parent_popup.dismiss()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        confirm_btn = PrimaryButton(text=prevedi("db_add_to_list_btn", jezik))
        confirm_btn.bind(on_release=confirm)
        cancel_btn = SecondaryButton(text=prevedi("sl_cancel", jezik))
        cancel_btn.bind(on_release=qty_popup.dismiss)
        btn_row.add_widget(confirm_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        qty_popup.open()

    def show_prodavnice(self):
        jezik = _jezik()
        box = self.ids.database_box
        box.clear_widgets()
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

    def go_back(self):
        self.manager.current = "home"

"""
Zajednicki stilizovani widget-i za "profi" izgled aplikacije.
Boja se automatski uzima iz app.theme.accent (vidi theme.py), pa se sve
dugmice u aplikaciji menjaju odjednom kad korisnik promeni temu u
Podesavanjima.
"""
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.lang import Builder
Builder.load_string("""
#:import dp kivy.metrics.dp
<PrimaryButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    bold: True
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.25)
        RoundedRectangle:
            pos: self.x, self.y - dp(2)
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: app.theme.accent if self.state == "normal" else (app.theme.accent[0]*0.7, app.theme.accent[1]*0.7, app.theme.accent[2]*0.7, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
<SecondaryButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.2)
        RoundedRectangle:
            pos: self.x, self.y - dp(2)
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: (0.28, 0.28, 0.30, 1) if self.state == "normal" else (0.38, 0.38, 0.40, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
<DangerButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.2)
        RoundedRectangle:
            pos: self.x, self.y - dp(2)
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: (0.75, 0.20, 0.20, 1) if self.state == "normal" else (0.55, 0.15, 0.15, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
<Card>:
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.2)
        RoundedRectangle:
            pos: self.x, self.y - dp(2)
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: (0.16, 0.16, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
<StyledTextInput>:
    background_normal: ""
    background_active: ""
    background_color: 0, 0, 0, 0
    foreground_color: 1, 1, 1, 1
    cursor_color: 1, 1, 1, 1
    hint_text_color: 0.85, 0.85, 0.85, 1
    padding: [dp(12), dp(12), dp(12), dp(12)]
    canvas.before:
        Color:
            rgba: (0.14, 0.14, 0.16, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
        Color:
            rgba: (1, 1, 1, 1) if self.focus else (0.75, 0.75, 0.75, 1)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(10))
            width: 1.2
<BackButton>:
    orientation: "horizontal"
    padding: [dp(14), 0, dp(10), 0]
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: (0.95, 0.55, 0.15, 1) if self.state == "normal" else (0.85, 0.45, 0.1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(25)]
        Color:
            rgba: 1, 1, 1, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(25))
            width: 1.5
    Label:
        text: "<"
        font_size: "22sp"
        bold: True
        color: 1, 1, 1, 1
        size_hint_x: None
        width: dp(18)
    Label:
        text: root.text
        font_size: "16sp"
        bold: True
        color: 1, 1, 1, 1
""")
class PrimaryButton(Button):
    pass
class SecondaryButton(Button):
    pass
class DangerButton(Button):
    pass
class Card(BoxLayout):
    pass
class StyledTextInput(TextInput):
    pass
class BackButton(ButtonBehavior, BoxLayout):
    """Dugme 'Nazad' istog oblika kao nazad_btn.png (narandzasta
    zaobljena pilula sa strelicom), ali tekst je prevodiv - ne zavisi
    od slike koja ima fiksan tekst ubacen u nju."""
    text = StringProperty("Nazad")

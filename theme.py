"""
Tema boja aplikacije. Theme je EventDispatcher pa kv fajlovi koji citaju
app.theme.accent (ili .bg_color / .input_text_color) automatski dobiju
novu boju kad se tema promeni - bez potrebe da se app restartuje.
"""
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

THEMES = {
    "Plava": (0.16, 0.50, 0.85, 1),
    "Zelena": (0.20, 0.62, 0.35, 1),
    "Ljubicasta": (0.52, 0.30, 0.78, 1),
    "Narandzasta": (0.90, 0.45, 0.15, 1),
    "Crvena": (0.80, 0.22, 0.22, 1),
    "Tirkizna": (0.10, 0.60, 0.60, 1),
}

DEFAULT_THEME = "Plava"

PALETA = {
    "Plava - svetla": (0.40, 0.65, 0.95, 1),
    "Plava": (0.16, 0.50, 0.85, 1),
    "Plava - tamna": (0.08, 0.30, 0.55, 1),
    "Teget": (0.05, 0.15, 0.35, 1),

    "Zelena - svetla": (0.45, 0.80, 0.45, 1),
    "Zelena": (0.20, 0.62, 0.35, 1),
    "Zelena - tamna": (0.10, 0.40, 0.20, 1),
    "Maslinasta": (0.20, 0.35, 0.15, 1),

    "Zuta": (0.95, 0.85, 0.15, 1),
    "Narandzasta": (0.90, 0.45, 0.15, 1),
    "Crvena": (0.80, 0.22, 0.22, 1),
    "Bordo": (0.45, 0.08, 0.12, 1),
    "Ljubicasta": (0.52, 0.30, 0.78, 1),
}

DEFAULT_BG = "Teget"
DEFAULT_INPUT_TEXT = "Zuta"


def _boje_su_slicne(boja1, boja2, tolerancija=0.12):
    r1, g1, b1, _ = boja1
    r2, g2, b2, _ = boja2
    razlika = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
    return razlika < tolerancija


class Theme(EventDispatcher):
    accent = ListProperty(THEMES[DEFAULT_THEME])
    name = StringProperty(DEFAULT_THEME)

    bg_color = ListProperty(PALETA[DEFAULT_BG])
    bg_name = StringProperty(DEFAULT_BG)

    input_text_color = ListProperty(PALETA[DEFAULT_INPUT_TEXT])
    input_text_name = StringProperty(DEFAULT_INPUT_TEXT)

    def set_theme(self, naziv):
        if naziv in THEMES:
            self.name = naziv
            self.accent = THEMES[naziv]

    def darker(self, factor=0.65):
        r, g, b, a = self.accent
        return (r * factor, g * factor, b * factor, a)

    def set_bg_color(self, naziv):
        if naziv not in PALETA:
            return False
        nova_boja = PALETA[naziv]
        if _boje_su_slicne(nova_boja, self.input_text_color):
            return False
        self.bg_name = naziv
        self.bg_color = nova_boja
        return True

    def set_input_text_color(self, naziv):
        if naziv not in PALETA:
            return False
        nova_boja = PALETA[naziv]
        if _boje_su_slicne(nova_boja, self.bg_color):
            return False
        self.input_text_name = naziv
        self.input_text_color = nova_boja
        return True

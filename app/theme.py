PRIMARY = "#55B900"
PRIMARY_HOVER = "#4FA600"
PRIMARY_PRESSED = "#479500"
PRIMARY_LIGHT = "#F2F7EE"

LIGHT = {
    "bg": "#FFFFFF",
    "panel": "#FFFFFF",
    "panel2": "#F5F6F7",
    "hover": "#F1F2F3",
    "menu_hover": "#F4F5F6",
    "menubar_hover": "#F2F3F4",
    "text": "#2F3441",
    "text_strong": "#111418",
    "muted": "#8A94A0",
    "border": "#E5E5E5",
    "border_soft": "#ECECEC",
    "card_border": "#E9EAEC",
    "card_border_hover": "#DCDEE1",
    "input_border": "#DDDFE2",
    "thumb": "#E9EBEE",
    "scroll_handle": "#D9DCE0",
    "scroll_handle_hover": "#C6CAD0",
}

DARK = {
    "bg": "#1E2228",
    "panel": "#232830",
    "panel2": "#2A3038",
    "hover": "#31363F",
    "menu_hover": "#31363F",
    "menubar_hover": "#31363F",
    "text": "#E6E9EC",
    "text_strong": "#F2F4F6",
    "muted": "#98A0AA",
    "border": "#383E47",
    "border_soft": "#343A42",
    "card_border": "#383E47",
    "card_border_hover": "#4A515C",
    "input_border": "#454C56",
    "thumb": "#333A44",
    "scroll_handle": "#454C56",
    "scroll_handle_hover": "#575F6B",
}

_state = {"dark": False}


def is_dark():
    return _state["dark"]


def colors():
    return DARK if _state["dark"] else LIGHT


def _qss(c):
    return f"""
* {{ font-family: 'Segoe UI'; }}
QMainWindow, QDialog {{ background:{c['bg']}; }}
QWidget#central {{ background:{c['bg']}; }}
QToolTip {{ background:{c['panel2']}; color:{c['text']}; border:1px solid {c['border']}; padding:4px 6px; }}

QMenuBar {{ background:{c['panel']}; border-bottom:1px solid {c['border_soft']}; }}
QMenuBar::item {{ padding:6px 10px; color:{c['text']}; background:transparent; }}
QMenuBar::item:selected {{ background:{c['menubar_hover']}; }}

QMenu {{ background:{c['panel']}; border:1px solid {c['border']}; border-radius:6px; padding:4px 0; }}
QMenu::item {{ padding:10px 28px 10px 16px; color:{c['text']}; background:transparent; }}
QMenu::item:selected {{ background:{c['menu_hover']}; }}
QMenu::item:disabled {{ color:{c['muted']}; }}
QMenu::separator {{ height:1px; background:{c['border_soft']}; margin:4px 8px; }}

QLineEdit {{ border:1px solid {c['input_border']}; border-radius:4px; padding:6px 8px;
 background:{c['panel']}; color:{c['text']}; }}
QLineEdit:focus {{ border-color:{PRIMARY}; }}

QPushButton {{ color:{c['text']}; }}
QPushButton#ddBtn {{ background:transparent; border:none; border-radius:4px; padding:0 6px; }}
QPushButton#ddBtn:hover {{ background:{c['hover']}; }}
QPushButton#ddBtn::menu-indicator {{ image:none; width:0; }}
QPushButton#ghostBtn {{ border:none; background:transparent; border-radius:4px; padding:7px; }}
QPushButton#ghostBtn:hover {{ background:{c['hover']}; }}
QPushButton#ghostBtn:pressed {{ background:{c['border_soft']}; }}

QScrollBar:vertical {{ background:transparent; width:10px; margin:2px; }}
QScrollBar::handle:vertical {{ background:{c['scroll_handle']}; border-radius:5px; min-height:30px; }}
QScrollBar::handle:vertical:hover {{ background:{c['scroll_handle_hover']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background:transparent; }}

QCheckBox {{ color:{c['text']}; spacing:8px; }}
QCheckBox::indicator {{ width:16px; height:16px; border:1px solid {c['input_border']};
 border-radius:3px; background:{c['panel']}; }}
QCheckBox::indicator:checked {{ border-color:{PRIMARY}; background-color:{PRIMARY}; }}

QSpinBox {{ border:1px solid {c['input_border']}; border-radius:4px; padding:4px 6px;
 background:{c['panel']}; color:{c['text']}; }}
QLabel#dialogTitle {{ font-size:15px; font-weight:600; color:{c['text']}; }}
"""


def apply_theme(app, dark=None):
    from PySide6.QtGui import QFont, QPalette, QColor
    if dark is not None:
        _state["dark"] = dark
    c = colors()
    app.setFont(QFont("Segoe UI", 10))
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(c["bg"]))
    pal.setColor(QPalette.WindowText, QColor(c["text"]))
    pal.setColor(QPalette.Base, QColor(c["panel"]))
    pal.setColor(QPalette.AlternateBase, QColor(c["panel2"]))
    pal.setColor(QPalette.Text, QColor(c["text"]))
    pal.setColor(QPalette.Button, QColor(c["panel"]))
    pal.setColor(QPalette.ButtonText, QColor(c["text"]))
    pal.setColor(QPalette.ToolTipBase, QColor(c["panel2"]))
    pal.setColor(QPalette.ToolTipText, QColor(c["text"]))
    pal.setColor(QPalette.Highlight, QColor(PRIMARY))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.PlaceholderText, QColor(c["muted"]))
    pal.setColor(QPalette.Disabled, QPalette.Text, QColor(c["muted"]))
    pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor(c["muted"]))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(c["muted"]))
    app.setPalette(pal)
    app.setStyleSheet(_qss(c))

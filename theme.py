"""Colors, sizes, fonts and the global Qt stylesheet."""
from string import Template

from PyQt6.QtGui import QFont, QFontDatabase

import resources

# ---- colors -------------------------------------------------------------
GREEN_DARK = "#0B4D3A"
GREEN_DEEP = "#064D3A"
GREEN_MID = "#0A5C45"
GREEN = "#077D5A"
GREEN_HOVER = "#066A4C"
GREEN_TITLE = "#0B5541"
GREEN_SOFT = "#E2F6EE"
GREEN_MINT = "#B3EBD9"
GOLD = "#F2C23C"
BLUE = "#4A90D9"
AMBER = "#B8862E"
RED = "#C9495A"
RED_DARK = "#B02A1E"
PURPLE = "#7457A6"

WHITE = "#FFFFFF"
CARD = "#F7FAF8"
CARD_HOVER = "#EAF5F0"
BORDER = "#DCE7E3"
FIELD_BORDER = "#C9D3CF"
TEXT = "#2B3632"
MUTED = "#6B7773"
PLACEHOLDER = "#A3ADA9"
NAV_ACTIVE = "#8FAAA0"

# ---- shape --------------------------------------------------------------
R_CARD = 26       # big panels and cards
R_FIELD = 16      # inputs
R_BTN = 22        # buttons (pill-ish)
FIELD_H = 40
BTN_H = 44
SIDEBAR_W = 280

_family = "Segoe UI"


def init_fonts(app):
    """Load any fonts in assets/fonts and pick the best available family."""
    global _family
    fonts = resources.ASSETS / "fonts"
    if fonts.exists():
        for f in list(fonts.glob("*.ttf")) + list(fonts.glob("*.otf")):
            QFontDatabase.addApplicationFont(str(f))
    available = set(QFontDatabase.families())
    for name in ("Poppins", "DM Sans", "Montserrat", "Segoe UI", "Helvetica Neue", "Arial"):
        if name in available:
            _family = name
            break
    else:
        _family = app.font().family()
    app.setFont(QFont(_family, 10))


def family():
    return _family


def script_family():
    available = set(QFontDatabase.families())
    for name in ("Segoe Script", "Brush Script MT", "Lucida Handwriting", "Z003"):
        if name in available:
            return name
    return _family


_QSS = Template("""
* { font-family: "$family"; color: $TEXT; }
QWidget#root, QWidget#page, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }
QLabel { background: transparent; }
QToolTip { background: $GREEN_DARK; color: white; border: none; padding: 4px 8px; }

/* ---------- cards ---------- */
QFrame#card { background: $WHITE; border: 2px solid $BORDER; border-radius: ${R_CARD_BIG}px; }
QFrame#tile { background: $CARD; border: 2px solid $BORDER; border-radius: ${R_CARD}px; }
QFrame#tile:hover { background: $CARD_HOVER; }
QFrame#statCard { background: $WHITE; border: 2px solid $BORDER; border-radius: ${R_CARD}px; }
QFrame#tableCard { background: $WHITE; border: 2px solid #CFE0D9; border-radius: ${R_CARD}px; }
QFrame#footer { background: $CARD; border: none; border-radius: 16px; }
QFrame#pill { background: $GREEN_SOFT; border: none; border-radius: 15px; }
QFrame#divider { background: $BORDER; border: none; }
QFrame#dialogBox { background: $WHITE; border: 2px solid #151A18; border-radius: 30px; }
QFrame#detailGrid { background: $CARD; border: 1px solid $BORDER; border-radius: 22px; }

/* ---------- inputs ---------- */
QLineEdit#field, QComboBox#field {
    background: $WHITE; border: 2px solid $FIELD_BORDER; border-radius: ${R_FIELD}px;
    padding: 0 14px; selection-background-color: $GREEN_MINT; selection-color: $TEXT;
}
QLineEdit#field:focus, QComboBox#field:focus, QComboBox#field:on { border-color: $GREEN; }
QLineEdit#field[error="true"], QComboBox#field[error="true"] { border-color: $RED; }
QLineEdit#field:disabled, QComboBox#field:disabled { background: #F2F5F4; color: #8A9692; border-color: #E1E7E5; }
QComboBox#field::drop-down {
    subcontrol-origin: padding; subcontrol-position: center right; width: 34px;
    border: none; border-top-right-radius: ${R_FIELD}px; border-bottom-right-radius: ${R_FIELD}px;
    background: #DCEBE4;
}
QComboBox#field::drop-down:disabled { background: #E9EEEC; }
QComboBox#field::down-arrow { image: url("$ARROW"); width: 14px; height: 14px; }
QComboBox QAbstractItemView {
    background: $WHITE; border: 2px solid $FIELD_BORDER; border-radius: 12px; padding: 6px; outline: none;
    selection-background-color: $GREEN_SOFT; selection-color: $GREEN_TITLE;
}
QComboBox QAbstractItemView::item { min-height: 30px; padding-left: 8px; border-radius: 8px; }

QFrame#iconEdit { background: $WHITE; border: 2px solid $FIELD_BORDER; border-radius: ${R_FIELD_BIG}px; }
QFrame#iconEdit[focus="true"] { border-color: $GREEN; }
QFrame#iconEdit[error="true"] { border-color: $RED; }
QFrame#iconEdit QLineEdit { background: transparent; border: none; padding: 0; }

/* ---------- buttons ---------- */
QPushButton { border: none; border-radius: ${R_BTN}px; padding: 0 22px; font-weight: 600; font-size: 14px; }
QPushButton[kind="primary"] { background: $GREEN; color: white; }
QPushButton[kind="primary"]:hover { background: $GREEN_HOVER; }
QPushButton[kind="dark"] { background: $GREEN_DARK; color: white; }
QPushButton[kind="dark"]:hover { background: #083B2C; }
QPushButton[kind="danger"] { background: $RED_DARK; color: white; }
QPushButton[kind="danger"]:hover { background: #8E2117; }
QPushButton[kind="outline"] { background: $WHITE; color: $GREEN_DARK; border: 2px solid $GREEN_DARK; }
QPushButton[kind="outline"]:hover { background: $CARD_HOVER; }
QPushButton[kind="ghost"] { background: transparent; color: $GREEN; padding: 0 8px; }
QPushButton[kind="ghost"]:hover { background: $CARD_HOVER; }
QPushButton[kind="link"] { background: transparent; color: $MUTED; font-weight: 400; font-size: 13px; padding: 0 4px; }
QPushButton[kind="link"]:hover { color: $GREEN; }
QPushButton:disabled { background: #D9E1DE; color: #8A9692; border-color: #D9E1DE; }
QPushButton[kind="page"] { background: #DDE8E3; color: $GREEN_TITLE; border-radius: 12px; padding: 0 6px; font-size: 12px; }
QPushButton[kind="page"]:hover { background: #CBDCD5; }
QPushButton[kind="page"][current="true"] { background: $GREEN; color: white; }
QPushButton[kind="page"]:disabled { background: #E7EEEB; color: #9DB0A8; }
QPushButton#eye { background: transparent; border-radius: 18px; padding: 0; }
QPushButton#eye:hover { background: $CARD_HOVER; }

QCheckBox { spacing: 9px; font-weight: 600; font-size: 12px; color: $MUTED; }
QCheckBox::indicator { width: 20px; height: 20px; border-radius: 7px; border: 2px solid $FIELD_BORDER; background: white; }
QCheckBox::indicator:checked { background: $GREEN; border-color: $GREEN; image: url("$CHECK"); }

/* ---------- table ---------- */
QTableWidget { background: transparent; border: none; outline: none; font-size: 12px; gridline-color: transparent;
    alternate-background-color: $GREEN_SOFT; selection-background-color: #BFE9D8; selection-color: $TEXT; }
QTableWidget::item { padding-left: 10px; border: none; }
QTableWidget[mode="view"]::item:hover { background: $GREEN_MINT; }
QHeaderView { background: transparent; border: none; }
QHeaderView::section { background: $GREEN_SOFT; color: $GREEN_TITLE; font-weight: 700; font-size: 12px;
    border: none; padding-left: 10px; height: 40px; }
QHeaderView::section:first { border-top-left-radius: 16px; border-bottom-left-radius: 16px; padding-left: 12px; }
QHeaderView::section:last { border-top-right-radius: 16px; border-bottom-right-radius: 16px; }

/* ---------- misc ---------- */
QProgressBar { background: $GREEN_SOFT; border: none; border-radius: 6px; max-height: 12px; min-height: 12px; }
QProgressBar::chunk { border-radius: 6px; background: $GREEN; }
QScrollBar:vertical { background: transparent; width: 12px; margin: 4px 0; }
QScrollBar::handle:vertical { background: #BFD3CB; border-radius: 5px; min-height: 40px; margin: 0 2px; }
QScrollBar::handle:vertical:hover { background: #9FBBB0; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QMenu { background: white; border: 2px solid $BORDER; border-radius: 12px; padding: 6px; }
QMenu::item { padding: 8px 26px; border-radius: 8px; }
QMenu::item:selected { background: $GREEN_SOFT; color: $GREEN_TITLE; }

QLabel#title { font-size: 36px; font-weight: 700; color: $GREEN_TITLE; }
QLabel#subtitle { font-size: 13px; color: $MUTED; }
QLabel#caption { font-size: 11px; font-weight: 600; color: $MUTED; }
QLabel#error { font-size: 12px; color: $RED; }
QLabel#ok { font-size: 12px; color: $GREEN; }
""")


def stylesheet(arrow_path, check_path):
    values = {k: v for k, v in globals().items() if k.isupper() and isinstance(v, str)}
    values.update(family=_family, R_CARD=R_CARD, R_CARD_BIG=R_CARD + 4, R_FIELD=R_FIELD,
                  R_FIELD_BIG=R_FIELD + 4, R_BTN=R_BTN, ARROW=arrow_path, CHECK=check_path)
    return _QSS.safe_substitute(values)

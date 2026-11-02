"""Reusable rounded widgets used across the app."""
from datetime import date

from PyQt6.QtCore import QEvent, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIntValidator
from PyQt6.QtWidgets import (QComboBox, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QWidget)

import icons
import theme as T

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]

_ICON_COLOR = {"primary": "#FFFFFF", "dark": "#FFFFFF", "danger": "#FFFFFF",
               "outline": T.GREEN_DARK, "ghost": T.GREEN, "link": T.MUTED}


def set_prop(widget, name, value):
    """Change a dynamic property and make the stylesheet pick it up."""
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def button(text, command=None, kind="primary", icon=None, width=150, height=T.BTN_H,
           icon_right=False):
    """kind: primary | dark | outline | danger | ghost | link"""
    if icon:                                     # Qt gives the icon almost no breathing room
        text = (text + "  ") if icon_right else ("  " + text)
    b = QPushButton(text)
    b.setProperty("kind", kind)
    b.setFixedHeight(height)
    if width:
        b.setMinimumWidth(width)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if icon:
        b.setIcon(icons.icon(icon, 20, _ICON_COLOR[kind]))
        b.setIconSize(QSize(20, 20))
        if icon_right:
            b.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    if command:
        b.clicked.connect(lambda _=False: command())
    return b


def shadow(widget, blur=36, dy=8, alpha=80):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setOffset(0, dy)
    eff.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(eff)


def hrow(*items, spacing=0, margins=(0, 0, 0, 0)):
    row = QHBoxLayout()
    row.setContentsMargins(*margins)
    row.setSpacing(spacing)
    for it in items:
        row.addWidget(it)
    return row


def page_header(title, subtitle, size=36):
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    t = QLabel(title)
    t.setObjectName("title")
    t.setStyleSheet(f"font-size: {size}px;")
    s = QLabel(subtitle)
    s.setObjectName("subtitle")
    lay.addWidget(t)
    lay.addWidget(s)
    return box


class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(e)


def make_transparent_to_mouse(widget):
    for child in widget.findChildren(QWidget):
        child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


# ---- inputs -------------------------------------------------------------
class IconLineEdit(QFrame):
    """Big rounded input with a leading icon (login screen and search boxes)."""
    returnPressed = pyqtSignal()

    def __init__(self, icon, placeholder, password=False, height=54):
        super().__init__()
        self.setObjectName("iconEdit")
        self.setFixedHeight(height)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 8 if password else 18, 0)
        lay.setSpacing(10)
        ico = QLabel()
        ico.setPixmap(icons.pixmap(icon, 22, "#555F5B"))
        lay.addWidget(ico)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setStyleSheet("font-size: 14px;")
        self.edit.installEventFilter(self)
        self.edit.returnPressed.connect(self.returnPressed)
        lay.addWidget(self.edit, 1)
        self._hidden = password
        if password:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye = QPushButton()
            self.eye.setObjectName("eye")
            self.eye.setFixedSize(36, 36)
            self.eye.setIconSize(QSize(22, 22))
            self.eye.setIcon(icons.icon("eye_off", 22, "#555F5B"))
            self.eye.setCursor(Qt.CursorShape.PointingHandCursor)
            self.eye.clicked.connect(self._toggle)
            lay.addWidget(self.eye)

    def eventFilter(self, obj, ev):
        if obj is self.edit and ev.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            set_prop(self, "focus", ev.type() == QEvent.Type.FocusIn)
        return super().eventFilter(obj, ev)

    def _toggle(self):
        self._hidden = not self._hidden
        self.edit.setEchoMode(QLineEdit.EchoMode.Password if self._hidden
                              else QLineEdit.EchoMode.Normal)
        self.eye.setIcon(icons.icon("eye_off" if self._hidden else "eye", 22, "#555F5B"))

    def text(self):
        """Passwords keep their spaces; everything else is trimmed."""
        return self.edit.text() if hasattr(self, "eye") else self.edit.text().strip()

    def setText(self, value):
        self.edit.setText(value)

    def clear(self):
        self.edit.clear()
        self.set_error(False)

    def setFocus(self):
        self.edit.setFocus()

    def set_error(self, flag=True):
        set_prop(self, "error", flag)


def _style_popup(combo):
    """Round the corners of a dropdown list (best effort, harmless if unsupported)."""
    try:
        win = combo.view().window()
        win.setWindowFlags(win.windowFlags() | Qt.WindowType.FramelessWindowHint
                           | Qt.WindowType.NoDropShadowWindowHint)
        win.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    except Exception:
        pass


def make_combo(values, height):
    c = QComboBox()
    c.setObjectName("field")
    c.setFixedHeight(height)
    c.addItems(values)
    c.setCurrentIndex(-1)
    c.setCursor(Qt.CursorShape.PointingHandCursor)
    _style_popup(c)
    return c


def make_edit(placeholder, height):
    e = QLineEdit()
    e.setObjectName("field")
    e.setFixedHeight(height)
    e.setPlaceholderText(placeholder)
    return e


class LabeledField(QWidget):
    """Small caption + rounded entry or dropdown, with an error state."""

    def __init__(self, label, kind="entry", values=None, required=False, placeholder="",
                 height=None):
        super().__init__()
        self.kind = kind
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        cap = QLabel(label + (" *" if required else ""))
        cap.setObjectName("caption")
        cap.setContentsMargins(8, 0, 0, 0)
        lay.addWidget(cap)
        h = height or T.FIELD_H
        if kind == "combo":
            self.widget = make_combo(values or [], h)
            self.widget.currentIndexChanged.connect(lambda _: self.set_error(False))
        else:
            self.widget = make_edit(placeholder, h)
            self.widget.textEdited.connect(lambda _: self.set_error(False))
        lay.addWidget(self.widget)

    def get(self):
        return (self.widget.currentText() if self.kind == "combo" else self.widget.text()).strip()

    def set(self, value):
        if self.kind == "combo":
            self.widget.setCurrentIndex(self.widget.findText(value or ""))
        else:
            self.widget.setText(value or "")

    def clear(self):
        self.set("")
        self.set_error(False)

    def set_enabled(self, flag):
        self.widget.setEnabled(flag)

    def set_error(self, flag=True):
        set_prop(self.widget, "error", flag)

    def focus(self):
        self.widget.setFocus()


class DateField(QWidget):
    """Month dropdown + day and year boxes. get() returns an ISO date string."""

    def __init__(self, label="Date of birth", required=True, height=None):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        cap = QLabel(label + (" *" if required else ""))
        cap.setObjectName("caption")
        cap.setContentsMargins(8, 0, 0, 0)
        lay.addWidget(cap)
        h = height or T.FIELD_H
        row = QHBoxLayout()
        row.setSpacing(6)
        self.month = make_combo(MONTHS, h)
        self.day = make_edit("Day", h)
        self.day.setValidator(QIntValidator(1, 31))
        self.day.setMaxLength(2)
        self.year = make_edit("Year", h)
        self.year.setValidator(QIntValidator(1900, 2100))
        self.year.setMaxLength(4)
        row.addWidget(self.month, 5)
        row.addWidget(self.day, 2)
        row.addWidget(self.year, 2)
        lay.addLayout(row)
        self.month.currentIndexChanged.connect(lambda _: self.set_error(False))
        self.day.textEdited.connect(lambda _: self.set_error(False))
        self.year.textEdited.connect(lambda _: self.set_error(False))

    def get(self):
        """'' if empty, ISO date if valid, ValueError with a friendly message otherwise."""
        m, d, y = self.month.currentIndex(), self.day.text().strip(), self.year.text().strip()
        if m < 0 and not d and not y:
            return ""
        if m < 0 or not d.isdigit() or not (y.isdigit() and len(y) == 4):
            raise ValueError("Enter a complete date of birth.")
        try:
            born = date(int(y), m + 1, int(d))
        except ValueError:
            raise ValueError("That date doesn't exist. Check the day and month.") from None
        if born > date.today() or born.year < 1900:
            raise ValueError("That date of birth doesn't look right.")
        return born.isoformat()

    def set(self, iso):
        self.clear()
        if iso:
            y, m, d = iso.split("-")
            self.month.setCurrentIndex(int(m) - 1)
            self.day.setText(str(int(d)))
            self.year.setText(y)

    def clear(self):
        self.month.setCurrentIndex(-1)
        self.day.clear()
        self.year.clear()
        self.set_error(False)

    def set_enabled(self, flag):
        for w in (self.month, self.day, self.year):
            w.setEnabled(flag)

    def set_error(self, flag=True):
        for w in (self.month, self.day, self.year):
            set_prop(w, "error", flag)

    def focus(self):
        self.month.setFocus()


def circle(diameter, bg, icon=None, icon_size=None, icon_color="#FFFFFF", border=None):
    """Round badge with an optional icon in the middle."""
    f = QFrame()
    f.setObjectName("badge")
    f.setFixedSize(diameter, diameter)
    edge = f"border: {border};" if border else "border: none;"
    f.setStyleSheet(f"QFrame#badge {{ background: {bg}; {edge} border-radius: {diameter // 2}px; }}")
    if icon:
        lay = QHBoxLayout(f)
        lay.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel()
        lbl.setPixmap(icons.pixmap(icon, icon_size or diameter // 2, icon_color))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)
    return f

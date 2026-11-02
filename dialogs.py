"""Rounded modal dialogs: confirm, message and resident details."""
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout,
                             QWidget)

import database as db
import icons
import theme as T
import widgets as W

MARGIN = 26   # transparent margin around the box, leaves room for the soft shadow


class Dialog(QDialog):
    def __init__(self, parent, width, height):
        super().__init__(parent.window() if parent else None)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.box = QFrame()
        self.box.setObjectName("dialogBox")
        W.shadow(self.box, 40, 10, 95)
        outer.addWidget(self.box)
        self.resize(width + MARGIN * 2, height + MARGIN * 2)

    def showEvent(self, e):
        super().showEvent(e)
        p = self.parentWidget()
        if p is not None:
            g = p.geometry()
            self.move(p.mapToGlobal(g.center() - g.topLeft()) - self.rect().center())


def _circle(icon, danger):
    return W.circle(104, "#F6D5D9" if danger else T.GREEN_MINT, icon, 48,
                    "#7A1F1A" if danger else "#3A6B5C")


def ask(parent, title, message, confirm="Yes", cancel="Cancel", icon="logout", danger=False,
        single=False):
    """The confirm dialog from the design. Returns True if the user confirmed."""
    dlg = Dialog(parent, 520, 340)
    lay = QVBoxLayout(dlg.box)
    lay.setContentsMargins(30, 30, 30, 28)
    lay.setSpacing(0)
    lay.addWidget(_circle(icon, danger), 0, Qt.AlignmentFlag.AlignHCenter)
    lay.addSpacing(10)
    t = QLabel(title)
    t.setAlignment(Qt.AlignmentFlag.AlignCenter)
    t.setStyleSheet(f"font-size: 28px; font-weight: 700; color: "
                    f"{T.RED_DARK if danger else T.GREEN};")
    lay.addWidget(t)
    m = QLabel(message)
    m.setAlignment(Qt.AlignmentFlag.AlignCenter)
    m.setWordWrap(True)
    m.setStyleSheet("font-size: 14px;")
    lay.addSpacing(8)
    lay.addWidget(m)
    lay.addStretch(1)
    row = QHBoxLayout()
    row.setSpacing(14)
    row.addStretch(1)
    if not single:
        row.addWidget(W.button(cancel, dlg.reject, "outline", width=190, height=50))
    row.addWidget(W.button(confirm, dlg.accept, "danger" if danger else "primary",
                           width=190, height=50))
    row.addStretch(1)
    lay.addLayout(row)
    return dlg.exec() == QDialog.DialogCode.Accepted


def info(parent, title, message, icon="check", danger=False):
    return ask(parent, title, message, confirm="OK", icon=icon, danger=danger, single=True)


def resident_details(parent, r, on_edit=None):
    """Read-only popup with every saved field. Calls on_edit(id) if Edit was pressed."""
    dlg = Dialog(parent, 660, 540)
    lay = QVBoxLayout(dlg.box)
    lay.setContentsMargins(30, 26, 30, 24)
    lay.setSpacing(10)

    top = QHBoxLayout()
    top.setSpacing(16)
    badge = W.circle(64, T.GREEN, "person", 34)
    top.addWidget(badge)
    names = QVBoxLayout()
    names.setSpacing(0)
    n = QLabel(db.full_name(r))
    n.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {T.GREEN_TITLE};")
    s = QLabel(f"Resident ID {db.fmt_id(r['id'])}")
    s.setObjectName("subtitle")
    names.addWidget(n)
    names.addWidget(s)
    top.addLayout(names, 1)
    lay.addLayout(top)

    grid_box = QFrame()
    grid_box.setObjectName("detailGrid")
    grid = QGridLayout(grid_box)
    grid.setContentsMargins(22, 16, 22, 16)
    grid.setHorizontalSpacing(30)
    grid.setVerticalSpacing(12)
    born = f"{r['birth_date']}  ({db.age_of(r['birth_date'])} yrs old)"
    items = [("Date of birth", born), ("Place of birth", r["birth_place"]),
             ("Sex", r["sex"]), ("Civil status", r["civil_status"]),
             ("Education", r["education"]), ("Occupation", r["occupation"]),
             ("Contact number", r["contact"]), ("Email", r["email"]), ("Address", r["address"])]
    for i, (label, value) in enumerate(items):
        cell = QWidget()
        cl = QVBoxLayout(cell)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        cap = QLabel(label.upper())
        cap.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {T.MUTED};")
        val = QLabel(value or "—")
        val.setWordWrap(True)
        val.setStyleSheet("font-size: 13px;")
        cl.addWidget(cap)
        cl.addWidget(val)
        last = i == len(items) - 1
        grid.addWidget(cell, i // 2, i % 2, 1, 2 if last else 1)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 1)
    lay.addWidget(grid_box, 1)

    row = QHBoxLayout()
    row.setSpacing(14)
    row.addStretch(1)
    wants_edit = []
    if on_edit:
        row.addWidget(W.button("Edit profile", lambda: (wants_edit.append(1), dlg.accept()),
                               "primary", icon="pencil", width=170, height=46))
    row.addWidget(W.button("Close", dlg.reject, "outline", width=150, height=46))
    row.addStretch(1)
    lay.addLayout(row)
    dlg.exec()
    if wants_edit and on_edit:
        on_edit(r["id"])
    return bool(wants_edit)

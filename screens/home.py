"""Home dashboard with the five shortcut cards."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QFrame

import database as db
import icons
import theme as T
import widgets as W

CARDS = [
    ("add", "Add New Profile", "Register a new resident in the barangay.", T.GREEN, "user_plus"),
    ("view", "View Resident Profile", "View and search resident records.", T.BLUE, "document"),
    ("update", "Update Profile", "Edit existing resident information.", T.AMBER, "pencil"),
    ("delete", "Delete Profile", "Remove a resident record from the system.", T.RED, "trash"),
    ("reports", "Reports", "View resident statistics and reports.", T.PURPLE, "bars"),
]


class HomePage(QWidget):
    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        top = QLabel("BARANGAY PROFILING SYSTEM")
        top.setObjectName("subtitle")
        lay.addWidget(top)
        title = QLabel("Welcome!")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 44px;")
        lay.addWidget(title)
        sub = QLabel("Manage resident records, monitor system activity, keep the barangay "
                     "data updated.")
        sub.setStyleSheet("font-size: 14px;")
        sub.setObjectName("subtitle")
        lay.addWidget(sub)
        lay.addSpacing(16)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        for i, (key, text, desc, color, icon) in enumerate(CARDS):
            last = i == len(CARDS) - 1
            grid.addWidget(self._card(key, text, desc, color, icon), i // 2, i % 2, 1,
                           2 if last else 1)
        lay.addLayout(grid)
        lay.addSpacing(12)
        lay.addWidget(self._summary(), 0, Qt.AlignmentFlag.AlignLeft)
        lay.addStretch(1)

    def _card(self, key, title, desc, color, icon):
        card = W.ClickableFrame()
        card.setObjectName("tile")
        card.setFixedHeight(112)
        row = QHBoxLayout(card)
        row.setContentsMargins(26, 0, 24, 0)
        row.setSpacing(18)
        row.addWidget(W.circle(70, color, icon, 36))
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addStretch(1)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 19px; font-weight: 700; color: {T.GREEN_TITLE};")
        d = QLabel(desc)
        d.setStyleSheet("font-size: 12px;")
        d.setWordWrap(True)
        col.addWidget(t)
        col.addWidget(d)
        col.addStretch(1)
        row.addLayout(col, 1)
        row.addWidget(W.circle(38, T.WHITE, "chevron_right", 16, "#333D39",
                               border=f"1px solid {T.FIELD_BORDER}"))
        W.make_transparent_to_mouse(card)
        card.clicked.connect(lambda k=key: self.shell.navigate(k))
        return card

    def _summary(self):
        s = db.statistics()
        text = (f"{s['total']} resident{'s' if s['total'] != 1 else ''} registered"
                f"   •   {s['new_this_month']} added this month")
        pill = QFrame()
        pill.setObjectName("pill")
        pill.setFixedHeight(32)
        pl = QHBoxLayout(pill)
        pl.setContentsMargins(18, 0, 18, 0)
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {T.GREEN_TITLE};")
        pl.addWidget(lbl)
        return pill

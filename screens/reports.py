"""Reports: headline numbers plus simple bar breakdowns, with CSV export."""
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QProgressBar,
                             QScrollArea, QVBoxLayout, QWidget)

import database as db
import dialogs
import theme as T
import widgets as W


class ReportsPage(QWidget):
    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        s = db.statistics()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QHBoxLayout()
        head.addWidget(W.page_header(
            "Reports", "Resident statistics at a glance. Numbers update as profiles are added, "
            "edited or removed."), 1)
        head.addWidget(W.button("Export CSV", self._export, icon="download", width=160, height=44),
                       0, Qt.AlignmentFlag.AlignBottom)
        lay.addLayout(head)
        lay.addSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setContentsMargins(0, 4, 8, 4)
        bl.setSpacing(12)
        scroll.setWidget(body)
        lay.addWidget(scroll, 1)

        if s["total"] == 0:
            empty = QLabel("No data yet. Register residents to see their statistics here.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setObjectName("subtitle")
            bl.addWidget(empty, 1)
            return

        kpis = QHBoxLayout()
        kpis.setSpacing(12)
        for label, value, color in [
                ("Total residents", s["total"], T.GREEN),
                ("Senior citizens (60+)", s["seniors"], T.PURPLE),
                ("Minors (under 18)", s["age"]["0-17"], T.BLUE),
                ("Added this month", s["new_this_month"], T.AMBER)]:
            kpis.addWidget(self._kpi(label, value, color), 1)
        bl.addLayout(kpis)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        cards = [
            ("Age groups", s["age"], T.GREEN),
            ("Sex", s["sex"], T.BLUE),
            ("Civil status", s["civil"], T.AMBER),
            ("Educational attainment", {k: s["education"][k] for k in db.EDUCATION
                                        if s["education"].get(k)}, T.PURPLE),
        ]
        for i, (title, counts, color) in enumerate(cards):
            grid.addWidget(self._breakdown(title, counts, color, s["total"]), i // 2, i % 2)
        grid.setRowStretch(2, 1)
        bl.addLayout(grid)
        bl.addStretch(1)

    def _kpi(self, label, value, color):
        card = QFrame()
        card.setObjectName("tile")
        card.setFixedHeight(92)
        row = QHBoxLayout(card)
        row.setContentsMargins(16, 16, 16, 16)
        row.setSpacing(14)
        bar = QFrame()
        bar.setFixedWidth(8)
        bar.setStyleSheet(f"background: {color}; border: none; border-radius: 4px;")
        row.addWidget(bar)
        col = QVBoxLayout()
        col.setSpacing(0)
        n = QLabel(str(value))
        n.setStyleSheet(f"font-size: 30px; font-weight: 700; color: {T.GREEN_TITLE};")
        t = QLabel(label)
        t.setObjectName("subtitle")
        t.setStyleSheet("font-size: 12px;")
        col.addWidget(n)
        col.addWidget(t)
        row.addLayout(col, 1)
        return card

    def _breakdown(self, title, counts, color, total):
        card = QFrame()
        card.setObjectName("statCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(8)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {T.GREEN_TITLE};")
        lay.addWidget(t)
        if not counts:
            m = QLabel("No data yet.")
            m.setObjectName("subtitle")
            lay.addWidget(m)
        for label, n in counts.items():
            row = QHBoxLayout()
            row.setSpacing(10)
            name = QLabel(label)
            name.setFixedWidth(140)
            name.setStyleSheet("font-size: 12px;")
            bar = QProgressBar()
            bar.setRange(0, 1000)
            bar.setValue(round(n * 1000 / total))
            bar.setTextVisible(False)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background: {color}; border-radius: 6px; }}")
            val = QLabel(f"{n}  ·  {round(n * 100 / total)}%")
            val.setFixedWidth(84)
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {T.GREEN_TITLE};")
            row.addWidget(name)
            row.addWidget(bar, 1)
            row.addWidget(val)
            lay.addLayout(row)
        lay.addStretch(1)
        return card

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export residents", f"residents_{date.today():%Y-%m-%d}.csv", "CSV file (*.csv)")
        if not path:
            return
        try:
            n = db.export_csv(path)
        except OSError as err:
            return dialogs.info(self, "Export failed", f"Couldn't write the file.\n{err}",
                                icon="warning", danger=True)
        dialogs.info(self, "Export complete", f"{n} resident record{'s' if n != 1 else ''} saved.")